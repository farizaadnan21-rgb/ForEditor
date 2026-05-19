using System;
using System.Drawing;
using System.Windows.Forms;

public partial class Form1 : Form
{
    // Deklarasi Bitmap sebagai canvas yang akan digunakan oleh semua fungsi
    private Bitmap canvasBitmap;

    public Form1()
    {
        InitializeComponent();
        InitializeCanvas();
    }

    private void InitializeCanvas()
    {
        // Set ukuran Bitmap sesuai ukuran PictureBox
        int width = drawingCanvas.Width;
        int height = drawingCanvas.Height;

        canvasBitmap = new Bitmap(width, height);
        drawingCanvas.Image = canvasBitmap;
        
        ClearScreen(); // Inisialisasi awal layar
    }

    // =========================================================
    // FUNGSI DASAR
    // =========================================================

    // Fungsi untuk menggambar satu piksel
    private void DrawPixel(int x, int y, Color c)
    {
        // Pastikan koordinat di dalam batas canvas
        if (x >= 0 && x < canvasBitmap.Width && y >= 0 && y < canvasBitmap.Height)
        {
            canvasBitmap.SetPixel(x, y, c);
        }
    }

    // Fungsi untuk membersihkan layar
    private void ClearScreen()
    {
        using (Graphics g = Graphics.FromImage(canvasBitmap))
        {
            g.Clear(Color.White); 
        }
        drawingCanvas.Refresh(); 
    }

    // Event handler untuk tombol Clear Screen
    private void btnClear_Click(object sender, EventArgs e)
    {
        ClearScreen();
    }

    // Event handler untuk Draw Pixel (Contoh sederhana)
    private void btnDrawPixel_Click(object sender, EventArgs e)
    {
        // Ambil koordinat x1 dan y1 sebagai titik
        if (int.TryParse(txtX1.Text, out int x) && int.TryParse(txtY1.Text, out int y))
        {
            DrawPixel(x, y, Color.Black);
            drawingCanvas.Refresh();
        }
    }

    // =========================================================
    // DRAW LINE MANUAL (Untuk Bagian 2)
    // =========================================================

    private void DrawManualLine(int x1, int y1, int x2, int y2, Color color)
    {
        float dx = x2 - x1;
        float dy = y2 - y1;
        float m = dy / dx; // Kemiringan

        float y = y1;
        
        for (int x = x1; x <= x2; x++)
        {
            // Panggil DrawPixel dengan nilai y yang dibulatkan
            DrawPixel(x, (int)Math.Round(y), color); 
            y += m; // Update y berdasarkan kemiringan
        }
    }

    private void btnDrawManualLine_Click(object sender, EventArgs e)
    {
        // Logika sederhana, tidak menangani semua oktant
        if (int.TryParse(txtX1.Text, out int x1) && int.TryParse(txtY1.Text, out int y1) &&
            int.TryParse(txtX2.Text, out int x2) && int.TryParse(txtY2.Text, out int y2))
        {
             // Asumsi: x2 > x1 dan kemiringan positif
            DrawManualLine(x1, y1, x2, y2, Color.Gray);
            drawingCanvas.Refresh();
        }
    }

    // =========================================================
    // DDA ALGORITHM (Floating Point)
    // =========================================================

    private void DrawDDALine(int x1, int y1, int x2, int y2, Color color)
    {
        float dx = x2 - x1;
        float dy = y2 - y1;

        // Tentukan steps
        float steps = Math.Max(Math.Abs(dx), Math.Abs(dy));

        // Hitung increment
        float x_inc = dx / steps;
        float y_inc = dy / steps;

        float x = x1;
        float y = y1;

        for (int i = 0; i <= steps; i++)
        {
            // Menggunakan Math.Round pada setiap langkah (operasional float)
            DrawPixel((int)Math.Round(x), (int)Math.Round(y), color); 
            
            x += x_inc;
            y += y_inc;
        }
    }

    private void btnDrawDDA_Click(object sender, EventArgs e)
    {
        if (int.TryParse(txtX1.Text, out int x1) && int.TryParse(txtY1.Text, out int y1) &&
            int.TryParse(txtX2.Text, out int x2) && int.TryParse(txtY2.Text, out int y2))
        {
            ClearScreen(); // Bersihkan layar untuk garis baru
            DrawDDALine(x1, y1, x2, y2, Color.Red); // DDA (Merah)
            drawingCanvas.Refresh();
        }
    }

    // =========================================================
    // BRESENHAM ALGORITHM (Integer Only)
    // =========================================================
    
    // Implementasi Bresenham (Hanya Oktant 1: 0 <= m <= 1)
    private void DrawBresenhamLine(int x1, int y1, int x2, int y2, Color color)
    {
        int dx = Math.Abs(x2 - x1);
        int dy = Math.Abs(y2 - y1);
        
        // Asumsi Oktant 1 (x2 > x1, y2 > y1, dan dx >= dy)
        if (dx >= dy)
        {
            int p = 2 * dy - dx; // Parameter Keputusan Awal
            int x = x1;
            int y = y1;

            for (int i = 0; i <= dx; i++)
            {
                DrawPixel(x, y, color);
                
                if (p < 0)
                {
                    p = p + 2 * dy; // Hanya penambahan integer
                }
                else
                {
                    y = y + 1; // Pindah ke y selanjutnya
                    p = p + 2 * dy - 2 * dx; // Hanya penambahan/pengurangan integer
                }
                x = x + 1;
            }
        }
        else // Kasus dy > dx (Oktant 2) harus diimplementasikan secara terpisah
        {
             // Anda harus menyelesaikan logika untuk semua oktant dalam laporan Anda
             MessageBox.Show("Implementasi ini hanya menangani kemiringan 0 <= m <= 1. Silakan coba koordinat yang sesuai.");
        }
    }

    private void btnDrawBresenham_Click(object sender, EventArgs e)
    {
        if (int.TryParse(txtX1.Text, out int x1) && int.TryParse(txtY1.Text, out int y1) &&
            int.TryParse(txtX2.Text, out int x2) && int.TryParse(txtY2.Text, out int y2))
        {
            // Untuk perbandingan berdampingan, Anda bisa tidak memanggil ClearScreen di sini
            // atau panggil fungsi DDA dan Bresenham dalam satu tombol gabungan.
            
            // Untuk demonstrasi mandiri:
            ClearScreen();
            DrawBresenhamLine(x1, y1, x2, y2, Color.Blue); // Bresenham (Biru)
            drawingCanvas.Refresh();
        }
    }
}