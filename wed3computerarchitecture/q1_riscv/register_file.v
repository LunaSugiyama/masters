// register_file.v
// RISC-V レジスタファイル

module register_file (
    input wire clk,
    input wire reg_write_en,      // レジスタ書き込みイネーブル
    input wire [4:0] rs1_addr,    // 読み出しアドレス1
    input wire [4:0] rs2_addr,    // 読み出しアドレス2
    input wire [4:0] rd_addr,     // 書き込みアドレス
    input wire [31:0] write_data, // 書き込みデータ
    output wire [31:0] read_data1,
    output wire [31:0] read_data2,
    output wire [31:0] x0_debug, x1_debug, x2_debug, x3_debug, x4_debug, x5_debug, x6_debug
);

    reg [31:0] registers [0:31]; // 32個の32ビットレジスタ

    // 初期化 (オプション: シミュレーション用に0クリア)
    integer i;
    initial begin
        for (i = 0; i < 32; i = i + 1) begin
            registers[i] = 32'h00000000;
        end
    end

    // 読み出しポート (組み合わせ回路)
    // x0 レジスタは常に0
    assign read_data1 = (rs1_addr == 5'h00) ? 32'h00000000 : registers[rs1_addr];
    assign read_data2 = (rs2_addr == 5'h00) ? 32'h00000000 : registers[rs2_addr];

    // 書き込みポート (同期回路)
    always @(posedge clk) begin
        if (reg_write_en) begin
            if (rd_addr != 5'h00) begin // x0 レジスタには書き込まない
                registers[rd_addr] <= write_data;
            end
        end
    end

    assign x0_debug = registers[0];
    assign x1_debug = registers[1];
    assign x2_debug = registers[2];
    assign x3_debug = registers[3];
    assign x4_debug = registers[4];
    assign x5_debug = registers[5];
    assign x6_debug = registers[6];

endmodule