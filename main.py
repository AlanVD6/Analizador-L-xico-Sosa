import tkinter as tk
def main():
    from interfaz import InterfazAnalizador
    root = tk.Tk()
    
    app = InterfazAnalizador(root)

    # Centrar ventana
    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.mainloop()
if __name__ == "__main__":
    main()