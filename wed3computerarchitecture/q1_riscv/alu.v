// alu.v
// 算術論理ユニット (ALU)

module alu (
    input wire [31:0] src_a,
    input wire [31:0] src_b,
    input wire [2:0]  alu_op, // 制御ユニットからのALU操作コード
    output reg [31:0] result
    // output wire zero_flag // 将来的にゼロフラグなども追加
);

    // ALU操作コードの定義 (例)
    localparam ALU_ADD  = 3'b000; // 加算
    localparam ALU_SUB  = 3'b001; // 減算
    localparam ALU_AND  = 3'b010; // 論理積
    localparam ALU_OR   = 3'b011; // 論理和
    localparam ALU_XOR  = 3'b100; // 排他的論理和
    localparam ALU_SLL  = 3'b101;
    localparam ALU_SRL  = 3'b110;
    localparam ALU_SRA  = 3'b111;
    // 他の命令 (SLL, SRL, SRA, SLT, SLTUなど) は必要に応じて追加

    always @(*) begin
        case (alu_op)
            ALU_ADD: result = src_a + src_b;
            ALU_SUB: result = src_a - src_b;
            ALU_AND: result = src_a & src_b;
            ALU_OR:  result = src_a | src_b;
            ALU_XOR: result = src_a ^ src_b;
            ALU_SLL: result = src_a << src_b[4:0];
            ALU_SRL: result = src_a >> src_b[4:0];
            ALU_SRA: result = $signed(src_a) >>> src_b[4:0];
            default: result = 32'hxxxxxxxx; // 未定義の場合
        endcase
    end

    // assign zero_flag = (result == 32'h00000000) ? 1'b1 : 1'b0;

endmodule