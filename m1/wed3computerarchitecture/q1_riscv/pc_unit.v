// // pc_unit.v
// // プログラムカウンタ

// module pc_unit (
//     input wire clk,
//     input wire reset,

//     input wire [31:0] imm_branch,  // 分岐・ジャンプのオフセット（符号付き）
//     input wire branch_taken,       // beq, bne が成功した場合 1
//     input wire jump_en,            // jal, jalr などジャンプ命令が有効な場合 1

//     output reg [31:0] pc_out       // 現在のPC
// );

//     wire [31:0] pc_plus4 = pc_out + 4;
//     wire [31:0] pc_branch_target = pc_out + imm_branch;

//     wire [31:0] next_pc =
//         (branch_taken || jump_en) ? pc_branch_target : pc_plus4;

//     always @(posedge clk or posedge reset) begin
//         if (reset) begin
//             pc_out <= 32'h00000000;
//         end else begin
//             pc_out <= next_pc;
//         end
//     end

// endmodule
// pc_unit.v

module pc_unit (
    input wire clk,
    input wire reset,
    input wire [31:0] next_pc_in,
    output reg [31:0] pc_out
);

    always @(posedge clk or posedge reset) begin
        if (reset)
            pc_out <= 32'h00000000;
        else
            pc_out <= next_pc_in;
    end

endmodule
