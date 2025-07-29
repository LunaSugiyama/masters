// riscv_single_cycle.v
// シングルサイクル RISC-V プロセッサのトップモジュール

module riscv_single_cycle (
    input wire clk,      // クロック
    input wire reset     // リセット
);

    // 内部信号の宣言
    wire [31:0] pc;                 // プログラムカウンタ
    wire [31:0] instruction;        // 命令
    wire [31:0] read_data1;         // レジスタファイルからの読み出しデータ1
    wire [31:0] read_data2;         // レジスタファイルからの読み出しデータ2
    wire [31:0] extended_immediate; // 符号拡張された即値
    wire [31:0] alu_result;         // ALUの出力
    reg  [31:0] write_data;         // レジスタファイルへの書き込みデータ  <--- CHANGED FROM 'wire' TO 'reg'
    wire [31:0] mem_read_data;      // データメモリからの読み出しデータwire [4:0]
    wire [4:0]  rs1_addr;           // ソースレジスタ1アドレス
    wire [4:0]  rs2_addr;           // ソースレジスタ2アドレス
    wire [4:0]  rd_addr;            // デスティネーションレジスタアドレス
    wire        reg_write_en;       // レジスタ書き込みイネーブル
    wire [2:0]  alu_op;             // ALU操作コード
    wire        alu_src_b;          // ALUのB入力選択（0: Reg, 1: Immediate）
    wire [1:0]  mem_to_reg;         // メモリからレジスタへのデータ選択
    wire        mem_read_en;        // データメモリ読み出しイネーブル // NEW: Added for data memory control
    wire        mem_write_en;       // データメモリ書き込みイネーブル // NEW: Added for data memory control
    wire        branch_taken;
    wire [31:0] imm_branch;
    wire [31:0] next_pc;
    wire [31:0] imm_u_type;
    wire [31:0] imm_j_type;

    // プログラムカウンタ (PC)
    // リセット時は0、それ以外はPC + 4
    pc_unit pc_unit_inst (
        .clk(clk),
        .reset(reset),
        .next_pc_in(next_pc),  // calculated next PC
        .pc_out(pc)            // current PC output
    );

    // 命令メモリ (Instruction Memory)
    instruction_memory im_inst (
        .addr(pc),
        .instruction_out(instruction)
    );

    always @(posedge clk) begin
        $display("DEBUG: Time=%0t | PC=%h | imm_branch=%h | branch_taken=%b", 
                $time, pc, imm_branch, branch_taken);
    end


    // 命令デコード
    // 命令から各フィールドを抽出
    assign rs1_addr = instruction[19:15];
    assign rs2_addr = instruction[24:20];
    assign rd_addr  = instruction[11:7];

    // GTKWAVEチェックのため
    wire [31:0] x0_debug, x1_debug, x2_debug, x3_debug, x4_debug, x5_debug, x6_debug;

    // レジスタファイル
    // rs1_addrとrs2_addrからデータを読み出し、rd_addrにwrite_dataを書き込む
    register_file rf_inst (
        .clk(clk),
        .reg_write_en(reg_write_en),
        .rs1_addr(rs1_addr),
        .rs2_addr(rs2_addr),
        .rd_addr(rd_addr),
        .write_data(write_data),
        .read_data1(read_data1),
        .read_data2(read_data2),
        .x0_debug(x0_debug),
        .x1_debug(x1_debug),
        .x2_debug(x2_debug),
        .x3_debug(x3_debug),
        .x4_debug(x4_debug),
        .x5_debug(x5_debug),
        .x6_debug(x6_debug)
    );

    // 即値生成ユニット (Sign Extender)
    // Iタイプ命令の即値を32ビットに符号拡張
    // 拡張性のため、他のタイプの即値生成もここに追加
    sign_extender se_inst (
        .instruction(instruction),
        .extended_immediate(extended_immediate),
        .imm_branch(imm_branch),
        .imm_u_type(imm_u_type),
        .imm_j_type(imm_j_type)
    );

    always @(posedge clk) begin
        $display("DEBUG: Time=%0t | PC=%h | imm_branch=%h | branch_taken=%b", 
                $time, pc, imm_branch, branch_taken);
    end


    // ALU (Arithmetic Logic Unit)
    // alu_src_bによってread_data2かextended_immediateを選択し演算
    alu alu_inst (
        .src_a(read_data1),
        .src_b(alu_b_input), // MUX for ALU B input
        .alu_op(alu_op),
        .result(alu_result)
    );

    // B-type
    wire [6:0] opcode = instruction[6:0];
    wire [2:0] funct3 = instruction[14:12];
    localparam OP_BRANCH = 7'b1100011;

    assign branch_taken = (opcode == OP_BRANCH) && (
        (funct3 == 3'b000 && alu_result == 0) ||  // beq
        (funct3 == 3'b001 && alu_result != 0)     // bne
    );

    // J-type
    wire jump_en = (opcode == 7'b1101111); // jal
    assign next_pc =
        jump_en        ? pc + imm_j_type :
        branch_taken   ? pc + imm_branch :
                        pc + 4;
 
    always @(posedge clk) begin
        $display("DEBUG: Time=%0t | PC=%h | imm_branch=%h | branch_taken=%b, next_pc=%h", 
                $time, pc, imm_branch, branch_taken, next_pc);
    end

    // U-type
    localparam OP_LUI = 7'b0110111;
    wire [31:0] alu_b_input = (opcode == OP_LUI) ? imm_u_type :
                            (alu_src_b ? extended_immediate : read_data2);



    // データメモリ (Data Memory) - Rタイプでは使用しないが、I/Sタイプで必要
    // 最初はダミーで置いておく
    data_memory dm_inst (
        .clk(clk),
        .addr(alu_result), // ロード/ストアアドレス
        .write_data(read_data2), // ストアデータ
        // .mem_read_en(1'b0),  // 後で制御ユニットから接続
        // .mem_write_en(1'b0), // 後で制御ユニットから接続
        // .read_data_out()     // ロードデータ (未使用だがポートは保持)
        .mem_read_en(mem_read_en),  // 制御ユニットから接続 // NEW: Connected
        .mem_write_en(mem_write_en),// 制御ユニットから接続 // NEW: Connected
        .read_data_out(mem_read_data) // ロードデータ // NEW: Connected to new wire
    );

    // ライトバックステージのMux // MODIFIED: Now a MUX
    // mem_to_reg 信号に基づいて、ALUの結果またはメモリからの読み出しデータを write_data として選択
    // mem_to_reg:
    // 00: ALU結果をレジスタに書き込む (R-type, I-type (addi))
    // 01: メモリからのデータをレジスタに書き込む (lw)
    // (他の値は将来の拡張用、例: PC+4 for JAL/JALR)
    always @* begin
        case (mem_to_reg)
            2'b00: write_data = (jump_en ? pc + 4 : alu_result);
            2'b01: write_data = mem_read_data;
            default: write_data = 32'b0;
        endcase
    end
    // // alu_resultをwrite_dataとして選択。後でメモリロードデータも選択肢に追加
    // assign write_data = alu_result;

    // 制御ユニット (Control Unit)
    // 命令から制御信号を生成
    control_unit cu_inst (
        .opcode(instruction[6:0]),
        .funct3(instruction[14:12]),
        .funct7(instruction[31:25]),
        .reg_write_en(reg_write_en),
        .alu_op(alu_op),
        .alu_src_b(alu_src_b),
        .mem_read_en(mem_read_en),  // Connected
        .mem_write_en(mem_write_en),// Connected
        .mem_to_reg(mem_to_reg)     // Connected// 他の制御信号 (Branch, Jump, PC_Sourceなど) は必要に応じて追加
    );

endmodule