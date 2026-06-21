// data_memory.v
module data_memory (
    input  wire        clk,
    input  wire [31:0] addr,
    input  wire [31:0] write_data,
    input  wire        mem_read_en,
    input  wire        mem_write_en,
    output reg  [31:0] read_data_out
);

    reg [31:0] mem [0:1023];
    integer i;

    initial begin
        for (i = 0; i < 1024; i = i + 1)
            mem[i] = 32'hDEAD_BEEF;
        mem[2] = 32'hDEAD_BEEF;
    end

    // 読み出し
    always @(*) begin
        if (mem_read_en) begin
            read_data_out = mem[addr[31:2]];
`ifdef DEBUG_MEM
            $display("[%0t] DMEM READ : addr=%h idx=%0d data=%h",
                     $time, addr, addr[31:2], read_data_out);
`endif
        end else begin
            read_data_out = 32'h0000_0000;
        end
    end

    // 書き込み（同期）
    always @(posedge clk) begin
        if (mem_write_en) begin
            mem[addr[31:2]] <= write_data;
`ifdef DEBUG_MEM
            $display("[%0t] DMEM WRITE: addr=%h idx=%0d data=%h",
                     $time, addr, addr[31:2], write_data);
`endif
        end
    end

endmodule
