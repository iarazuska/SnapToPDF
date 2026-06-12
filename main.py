from tkinterdnd2 import TkinterDnD
from ui import SnapToPDFApp

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SnapToPDFApp(root)
    root.mainloop()