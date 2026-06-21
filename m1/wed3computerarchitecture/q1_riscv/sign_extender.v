// sign_extender.v
// 即値生成・符号拡張ユニット
// 将来的には他の命令フォーマットにも対応させる

module sign_extender (
    input wire [31:0] instruction,
    output wire [31:0] extended_immediate,
    output wire [31:0] imm_branch,
    output wire [31:0] imm_u_type,
    output wire [31:0] imm_j_type
);
    // B-type
    assign imm_branch = {{19{instruction[31]}}, instruction[31], instruction[7],
                     instruction[30:25], instruction[11:8], 1'b0};

    // Iタイプ命令の即値 (instruction[31:20]) を符号拡張
    // RISC-Vは下位12ビットの即値の場合、上位20ビットを最上位ビットで埋める
    assign extended_immediate = {{20{instruction[31]}}, instruction[31:20]};

    // U type
    assign imm_u_type = {instruction[31:12], 12'b0};

    // J type
    assign imm_j_type = {{12{instruction[31]}}, instruction[19:12], instruction[20], instruction[30:21], 1'b0};

endmodule