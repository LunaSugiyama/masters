// testbench.v
// riscv_single_cycle のテストベンチ

`timescale 1ns / 1ps

module testbench;

    reg clk;
    reg reset;

    // riscv_single_cycle インスタンス
    riscv_single_cycle uut (
        .clk(clk),
        .reset(reset)
    );

    // クロック生成
    always begin
        #5 clk = ~clk; // 10ns周期 (100MHz)
    end

    // 初期化とテストシーケンス
    initial begin
        clk = 1'b0;
        reset = 1'b1; // リセットをかける
        #20 reset = 1'b0; // リセット解除

        // プロセッサが数サイクル動作するのを待つ
        // instruction_memory に記述した命令が実行される
        #100;

        // 特定のレジスタ値をチェックするなど、より詳細なテストを追加可能
        // 例: レジスタファイルからの読み出し信号をダンプ波形に出力するなど

        $display("Test finished.");
        $finish; // シミュレーション終了
    end

    // 波形出力 (GTKWaveなどで確認するため)
    integer k;
    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, testbench.uut);
    end

endmodule