import tkinter.filedialog

fn = tkinter.filedialog.askopenfilename()

f = open(fn)
data = f.read()
f.close()

f = open(fn, "w")
f.write(data[3:])
f.close()

input()
