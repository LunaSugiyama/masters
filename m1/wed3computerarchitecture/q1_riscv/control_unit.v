// control_unit.v
// 制御ユニット

module control_unit (
    input wire [6:0] opcode,
    input wire [2:0] funct3,
    input wire [6:0] funct7,
    output reg reg_write_en,    // レジスタファイル書き込みイネーブル
    output reg [2:0] alu_op,     // ALU操作コード
    output reg alu_src_b,       // ALUのB入力選択 (0: Reg, 1: Immediate)
    output reg mem_read_en,     // データメモリ読み出しイネーブル
    output reg mem_write_en,    // データメモリ書き込みイネーブル
    output reg [1:0] mem_to_reg // メモリからレジスタへのデータ選択
    // 他の制御信号 (Branch, Jump, PC_Sourceなど) は必要に応じて追加
);

    // RISC-V Opcode の定義 (一部)
    localparam OP_R_TYPE = 7'b0110011; // Rタイプ命令 (add, sub, and, or, xorなど)
    localparam OP_IMM    = 7'b0010011; // Iタイプ即値命令 (addi, andiなど)
    localparam OP_LOAD   = 7'b0000011; // ロード命令 (lwなど)
    localparam OP_STORE  = 7'b0100011; // ストア命令 (swなど)
    localparam OP_BRANCH = 7'b1100011; // Bタイプ（beq, bne など）
    localparam OP_LUI    = 7'b0110111; // Uタイプ（lui）
    localparam OP_JAL    = 7'b1101111; // Jタイプ（jal）

    // ALU操作コード (ALU.vと同期)
    localparam ALU_ADD  = 3'b000;
    localparam ALU_SUB  = 3'b001;
    localparam ALU_AND  = 3'b010;
    localparam ALU_OR   = 3'b011;
    localparam ALU_XOR  = 3'b100;
    localparam ALU_SLL  = 3'b101;
    localparam ALU_SRL  = 3'b110;
    localparam ALU_SRA  = 3'b111;

    // mem_to_reg の定義
    localparam MEM2REG_ALU_RESULT = 2'b00;
    localparam MEM2REG_MEM_DATA   = 2'b01;


    always @(*) begin
        // デフォルト値 (安全のため)
        reg_write_en = 1'b0;
        alu_op       = ALU_ADD; // デフォルトは加算としておく
        alu_src_b    = 1'b0;    // デフォルトはレジスタ2
        mem_read_en  = 1'b0;
        mem_write_en = 1'b0;
        mem_to_reg   = MEM2REG_ALU_RESULT;

        case (opcode)
            OP_R_TYPE: begin // Rタイプ命令 (add, sub, and, or, xorなど)
                reg_write_en = 1'b1;
                alu_src_b    = 1'b0; // ALUのB入力はレジスタ2
                mem_read_en  = 1'b0;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_ALU_RESULT;
                case ({funct7, funct3}) // funct7 と funct3 でALU操作を決定
                    // add (funct7=0x00, funct3=0x0)
                    {7'h00, 3'b000}: alu_op = ALU_ADD;
                    // sub (funct7=0x20, funct3=0x0)
                    {7'h20, 3'b000}: alu_op = ALU_SUB;
                    // and (funct7=0x00, funct3=0x7)
                    {7'h00, 3'b111}: alu_op = ALU_AND;
                    // or  (funct7=0x00, funct3=0x6)
                    {7'h00, 3'b110}: alu_op = ALU_OR;
                    // xor (funct7=0x00, funct3=0x4)
                    {7'h00, 3'b100}: alu_op = ALU_XOR;
                    // sll (funct7=0x00, funct3=0x1)
                    {7'h00, 3'b001}: alu_op = ALU_SLL;
                    // srl (funct7=0x00, funct3=0x5)
                    {7'h00, 3'b101}: alu_op = ALU_SRL;
                    // sra (funct7=0x20, funct3=0x5)
                    {7'h20, 3'b101}: alu_op = ALU_SRA;
                    default: begin
                        // 未サポートのRタイプ命令
                        alu_op = ALU_ADD; // デフォルト
                    end
                endcase
            end
            OP_IMM: begin // addi, andi など
                reg_write_en = 1'b1;
                alu_src_b    = 1'b1; // ALUのB入力は即値
                mem_read_en  = 1'b0;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_ALU_RESULT;
                case (funct3)
                    3'b000: alu_op = ALU_ADD; // addi
                    3'b111: alu_op = ALU_AND; // andi
                    3'b001: alu_op = ALU_SLL; // slli
                    3'b101: begin // srli or srai
                    // Check funct7[5] (which corresponds to instruction bit 30)
                    if (funct7[5] == 1'b1) begin
                        alu_op = ALU_SRA; // srai
                    end else begin
                        alu_op = ALU_SRL; // srli
                    end
                end// 他のIタイプ命令
                    default: alu_op = ALU_ADD;
                endcase
            end
            OP_LOAD: begin // lw など
                reg_write_en = 1'b1;
                alu_src_b    = 1'b1; // アドレス計算に即値を使用
                mem_read_en  = 1'b1;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_MEM_DATA;
                alu_op       = ALU_ADD; // ベースアドレス + オフセット
            end
            OP_STORE: begin // sw など
                reg_write_en = 1'b0;
                alu_src_b    = 1'b1; // アドレス計算に即値を使用
                mem_read_en  = 1'b0;
                mem_write_en = 1'b1;
                mem_to_reg   = MEM2REG_ALU_RESULT; // 関係ないがデフォルト
                alu_op       = ALU_ADD; // ベースアドレス + オフセット
            end
            OP_BRANCH: begin
                reg_write_en = 1'b0;
                alu_src_b    = 1'b0; // 比較は2つのレジスタ間
                mem_read_en  = 1'b0;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_ALU_RESULT;
                case (funct3)
                    3'b000: alu_op = ALU_SUB; // beq: x == y → x - y == 0
                    3'b001: alu_op = ALU_SUB; // bne: x != y → x - y != 0
                    default: alu_op = ALU_SUB; // 他の比較命令（未実装なら一旦SUB）
                endcase
                // 分岐制御信号 (別途 branch_taken などの生成が必要)
            end
            OP_LUI: begin
                reg_write_en = 1'b1;
                alu_src_b    = 1'b1;  // 無視されるが一応設定
                mem_read_en  = 1'b0;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_ALU_RESULT;
                alu_op       = ALU_ADD; // ALUは不要だが、0 + immの形にしてもよい
            end
            OP_JAL: begin
                reg_write_en = 1'b1;
                alu_src_b    = 1'b0; // PC + 4 → rd
                mem_read_en  = 1'b0;
                mem_write_en = 1'b0;
                mem_to_reg   = MEM2REG_ALU_RESULT;
                alu_op       = ALU_ADD; // PC + 4 (ただし別ロジックで)
            end
        default: begin
                // 未サポートの命令
            end
        endcase
    end

endmodule