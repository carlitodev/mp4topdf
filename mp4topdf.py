import os
from tkinter import *
from tkinter import filedialog, messagebox
from moviepy.editor import VideoFileClip
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class VideoToPDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Video to PDF Converter")

        self.label = Label(master, text="Select Video File:")
        self.label.grid(row=0, column=0, sticky=W, padx=10, pady=10)

        self.video_entry = Entry(master, width=50)
        self.video_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = Button(master, text="Browse", command=self.browse_video)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.label2 = Label(master, text="Screenshot Time Interval (seconds):")
        self.label2.grid(row=1, column=0, sticky=W, padx=10, pady=10)

        self.time_entry = Entry(master)
        self.time_entry.grid(row=1, column=1, padx=10, pady=10)

        self.label3 = Label(master, text="Select Output Folder:")
        self.label3.grid(row=2, column=0, sticky=W, padx=10, pady=10)

        self.folder_entry = Entry(master, width=50)
        self.folder_entry.grid(row=2, column=1, padx=10, pady=10)

        self.browse_button2 = Button(master, text="Browse", command=self.browse_folder)
        self.browse_button2.grid(row=2, column=2, padx=10, pady=10)

        self.convert_button = Button(master, text="Convert to PDF", command=self.convert_to_pdf)
        self.convert_button.grid(row=3, column=1, padx=10, pady=20)

    def browse_video(self):
        video_file = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if video_file:
            self.video_entry.delete(0, END)
            self.video_entry.insert(0, video_file)

    def browse_folder(self):
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.folder_entry.delete(0, END)
            self.folder_entry.insert(0, output_folder)

    def convert_to_pdf(self):
        video_path = self.video_entry.get()
        screenshot_interval = float(self.time_entry.get().strip())
        output_folder = self.folder_entry.get()

        if not video_path or not os.path.isfile(video_path):
            messagebox.showerror("Error", "Please select a valid video file.")
            return

        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Please select a valid output folder.")
            return

        try:
            video = VideoFileClip(video_path)
            duration = video.duration
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
            return

        output_pdf = os.path.join(output_folder, f"screenshots_{os.path.basename(video_path).split('.')[0]}.pdf")
        width, height = letter
        c = canvas.Canvas(output_pdf, pagesize=letter)

        for t in range(0, int(duration), int(screenshot_interval)):
            try:
                frame = video.get_frame(t)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract frame at {t} seconds: {str(e)}")
                return

            # Save frame as temporary image file (PNG)
            temp_image_path = os.path.join(output_folder, f"screenshot_{t}.png")
            Image.fromarray(frame).save(temp_image_path)

            # Calculate dimensions to fit the image into the PDF
            image = Image.open(temp_image_path)
            image_width, image_height = image.size
            aspect_ratio = image_width / image_height

            if aspect_ratio > 1:
                pdf_image_width = width
                pdf_image_height = width / aspect_ratio
            else:
                pdf_image_height = height
                pdf_image_width = height * aspect_ratio

            x_offset = (width - pdf_image_width) / 2
            y_offset = (height - pdf_image_height) / 2

            c.drawInlineImage(temp_image_path, x_offset, y_offset, pdf_image_width, pdf_image_height)
            c.showPage()

            # Clean up temporary image file
            os.remove(temp_image_path)

        c.save()
        messagebox.showinfo("Success", f"Screenshots saved to {output_pdf}")

if __name__ == "__main__":
    root = Tk()
    converter = VideoToPDFConverter(root)
    root.mainloop()
