using System;
using System.Drawing;
using System.Windows.Forms;
using System.Diagnostics; 
using System.Threading;

namespace MyGrafikaApp 
{
    public partial class Form1 : Form 
    {
        // Deklarasi Global yang PENTING:
        private Bitmap bitmap;
        private PictureBox canvas; 

        // Variabel tambahan lain yang tidak dipakai (seperti txtX1, btnDDA, dll.) kita hapus 
        // agar kode lebih bersih dan tidak menimbulkan error CS8618.
        
        public Form1()
        {
            // PENTING: InitializeComponent() harus dipanggil pertama kali jika ada Designer
            InitializeComponent(); 
            this.Text = "Grafika Komputer Assignment 1";
            this.Size = new Size(800, 600); // Sesuaikan ukuran Form agar muat

            // --- 1. INISIALISASI CANVAS ---
            canvas = new PictureBox
            {
                Name = "canvas",
                Size = new Size(500, 500),
                Location = new Point(10, 10),
                BackColor = Color.White,
                BorderStyle = BorderStyle.FixedSingle
            };
            this.Controls.Add(canvas);
            
            // Inisialisasi Bitmap (Harus setelah canvas diinisialisasi)
            bitmap = new Bitmap(canvas.Width, canvas.Height);
            canvas.Image = bitmap;

            // --- 2. INISIALISASI TOMBOL ANALISIS ---
            
            // Tombol Analisis/Uji Coba
            Button btnAnalyze = new Button { Text = "RUN ANALISIS", Location = new Point(520, 10), AutoSize = true };
            btnAnalyze.Click += btnAnalyze_Click;
            this.Controls.Add(btnAnalyze);
            
            // Tombol Bersihkan
            Button btnClear = new Button { Text = "Clear Screen", Location = new Point(520, 50), AutoSize = true };
            btnClear.Click += btnClearScreen_Click;
            this.Controls.Add(btnClear);
            
            // Tambahkan Label Hasil Analisis (opsional, untuk menampilkan hasil tanpa MessageBox)
            Label lblResult = new Label { Name = "lblResult", Location = new Point(520, 150), Size = new Size(250, 100), Text = "Tekan RUN ANALISIS untuk menguji 1000x." };
            this.Controls.Add(lblResult);
        }

        // =================================================================================
        // BAGIAN 2: DRAW PIXEL & CLEAR SCREEN
        // =================================================================================
        
        // 2A. Method DrawPixel
        private void DrawPixel(int x, int y, Color c)
        {
            if (x >= 0 && x < bitmap.Width && y >= 0 && y < bitmap.Height)
            {
                // Gunakan lock untuk menghindari masalah thread saat menggambar cepat
                lock (bitmap)
                {
                   bitmap.SetPixel(x, y, c);
                }
            }
        }
        
        // Clear Screen
        private void ClearScreen()
        {
            using (Graphics g = Graphics.FromImage(bitmap))
            {
                g.Clear(canvas.BackColor); 
            }
            canvas.Invalidate(); 
        }

        // =================================================================================
        // BAGIAN 3: ALGORITMA LINE DRAWING (Fungsi Mengembalikan Waktu)
        // =================================================================================

        // 3A. DDA Algorithm
        private long DrawLine_DDA(int x1, int y1, int x2, int y2, Color c)
        {
            float dx = x2 - x1;
            float dy = y2 - y1;
            
            if (dx == 0 && dy == 0) 
            {
                 DrawPixel(x1, y1, c); 
                 return 0;
            }
            
            int steps = (int)Math.Max(Math.Abs(dx), Math.Abs(dy));
            float x_inc = dx / steps;
            float y_inc = dy / steps;
            float x = x1;
            float y = y1;

            Stopwatch stopwatch = Stopwatch.StartNew(); 

            for (int i = 0; i <= steps; i++)
            {
                DrawPixel((int)Math.Round(x), (int)Math.Round(y), c); 
                x += x_inc;
                y += y_inc;
            }
            
            stopwatch.Stop(); 
            return stopwatch.ElapsedMilliseconds; 
        }

        // 3B. Bresenham Algorithm (untuk |m| <= 1. Tambahkan pengecekan m>1 agar stabil)
        private long DrawLine_Bresenham(int x1, int y1, int x2, int y2, Color c)
        {
            // Periksa jika m > 1, jika ya, tukar x dan y (transposisi)
            bool steep = Math.Abs(y2 - y1) > Math.Abs(x2 - x1);
            if (steep)
            {
                (x1, y1) = (y1, x1);
                (x2, y2) = (y2, x2);
            }

            // Urutkan x agar x1 selalu lebih kecil dari x2
            if (x1 > x2)
            {
                (x1, x2) = (x2, x1);
                (y1, y2) = (y2, y1);
            }

            int dx = x2 - x1;
            int dy = Math.Abs(y2 - y1);
            int sy = (y1 < y2) ? 1 : -1;
            int p = 2 * dy - dx; // Parameter keputusan awal
            int two_dy = 2 * dy;
            int two_dy_minus_dx = 2 * (dy - dx);
            int x = x1;
            int y = y1;

            Stopwatch stopwatch = Stopwatch.StartNew(); 

            // Loop utama
            for (int i = 0; i <= dx; i++)
            {
                // Jika steeping, tukar koordinat saat menggambar
                if (steep)
                {
                    DrawPixel(y, x, c); 
                }
                else
                {
                    DrawPixel(x, y, c);
                }

                if (p >= 0)
                {
                    y += sy;
                    p += two_dy_minus_dx; 
                }
                else
                {
                    p += two_dy; 
                }
                
                x++; 
            }
            
            stopwatch.Stop(); 
            return stopwatch.ElapsedMilliseconds;
        }

        // =================================================================================
        // BAGIAN 4: ANALISIS DAN EVENT HANDLER
        // =================================================================================

        private void btnAnalyze_Click(object? sender, EventArgs? e) 
        {
            // Tampilkan loading sebelum memulai analisis
            Label? lblResult = (Label?)this.Controls["lblResult"];
            if (lblResult != null) lblResult.Text = "Analisis berjalan... Mohon tunggu.";
            
            Application.DoEvents(); // Memaksa UI untuk refresh

            // Koordinat Uji: Garis Diagonal Panjang (dari kiri atas ke kanan bawah)
            int x1 = 10, y1 = 10, x2 = 490, y2 = 480; 
            int runs = 1000; 
            long totalTimeDDA = 0;
            long totalTimeBresenham = 0;

            ClearScreen();
            
            // Loop Uji Coba Kecepatan (dengan Color.Transparent agar CPU fokus pada perhitungan)
            for (int i = 0; i < runs; i++)
            {
                totalTimeDDA += DrawLine_DDA(x1, y1, x2, y2, Color.Transparent); 
                totalTimeBresenham += DrawLine_Bresenham(x1, y1, x2, y2, Color.Transparent);
            }
            
            long avgDDA = totalTimeDDA / runs;
            long avgBresenham = totalTimeBresenham / runs;
            
            // Gambar hasil visual perbandingan akhir (DDA dan Bresenham berdampingan)
            ClearScreen();
            DrawLine_DDA(x1, y1, x2, y2, Color.Red); // DDA
            DrawLine_Bresenham(x1, y1 + 5, x2, y2 + 5, Color.Blue); // Bresenham digeser 5 piksel ke bawah

            // Tampilkan hasil analisis
            string results = $"Analisis Selesai ({runs}x Pengujian):\n" +
                             $"Rata-rata Waktu DDA: {avgDDA} ms\n" +
                             $"Rata-rata Waktu Bresenham: {avgBresenham} ms\n\n" +
                             $"Hasil visual ditampilkan di canvas.";
                             
            if (lblResult != null) lblResult.Text = results;
            // MessageBox.Show(results, "Hasil Analisis Kinerja");

            canvas.Invalidate();
        }

        private void btnClearScreen_Click(object? sender, EventArgs? e)
        {
            ClearScreen();
            Label? lblResult = (Label?)this.Controls["lblResult"];
            if (lblResult != null) lblResult.Text = "Canvas dibersihkan. Tekan RUN ANALISIS.";
        }
    }
}