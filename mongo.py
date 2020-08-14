from datetime import datetime
from tkinter.ttk import Combobox

from mongoengine import *

from tkinter import *

global enter_date
global _plate

root = Tk()
root.minsize(450, 300)
root.title("CarPark Automation")

labels_frame = Frame(root, width=200)
labels_frame.grid(row=1, column=1, sticky=W + E)

res_label = Frame(root, width=200)
res_label.grid(row=1, column=2, sticky=W + E)

listbox = Listbox(root)
# listbox.pack(side=LEFT)
listbox.grid(column=0, row=1, padx=5, pady=5)

plate_label = Label(labels_frame, text='Plate Number: ', anchor='w')
enter_label = Label(labels_frame, text='Enter Date: ', anchor='w')
exit_label = Label(labels_frame, text='Exit Date: ', anchor='w')
price_label = Label(labels_frame, text='Price: ', anchor='w')

ll_res = Label(res_label, text='placeholder', anchor='w')
enl_res = Label(res_label, text='placeholder', anchor='w')
exl_res = Label(res_label, text='placeholder', anchor='w')
pl_res = Label(res_label, text='placeholder', anchor='w')

count_label = Label(root, text="count")
count = 0


def clicked():
    cal_btn.configure(state='disabled')
    root.after(500, get_data)
    _now = datetime.now()
    _dt_string = _now.strftime("%d/%m/%Y %H:%M:%S")
    _diff = _now - enter_date
    _days = int(_diff.days)
    _hours = int(_diff.seconds // (60 * 60))
    _new_price = 6 + (_days * 100 + _hours * 6)
    exl_res.configure(text=_dt_string)
    pl_res.configure(text=_new_price)
    Car.objects(plate_number=_plate).update(exit=now, price=_new_price)


def refresh_clicked():
    root.after(500, get_data('refresh'))


cal_btn = Button(root, text="Calculate Price", command=clicked, state='disabled')
refresh_button = Button(root, text="Refresh", command=refresh_clicked, state='normal')

n = StringVar()
coltbox = Combobox(root, textvariable=n, state='readonly')

coltbox.grid(column=0, row=0, padx=5, pady=5)

coltbox['values'] = ('All', 'In', 'Out')
coltbox.current(0)

plate_label.grid(sticky=W, column=1, padx=5, pady=5)
enter_label.grid(sticky=W, column=1, padx=5, pady=5)
exit_label.grid(sticky=W, column=1, padx=5, pady=5)
price_label.grid(sticky=W, column=1, padx=5, pady=5)

ll_res.grid(sticky=W, column=2, padx=5, pady=5)
enl_res.grid(sticky=W, column=2, padx=5, pady=5)
exl_res.grid(sticky=W, column=2, padx=5, pady=5)
pl_res.grid(sticky=W, column=2, padx=5, pady=5)
count_label.grid(column=1, row=0)

cal_btn.grid(column=1, row=2, padx=5, pady=5)
refresh_button.grid(column=0, row=2, padx=5, pady=5)


class Car(Document):
    plate_number = StringField(required=True, max_length=200)
    enter = DateTimeField(required=True, default=datetime.now)
    exit = DateTimeField()
    price = DecimalField(required=True)
    meta = {'collection': 'LicensePlates'}
    # published = DateTimeField(default=datetime.datetime.now)


# noinspection PyBroadException
try:
    connect(
        db='CarParkDB',
        host="mongodb+srv://USERNAME:PASSWORD.@cluster0-oj2fr.mongodb.net/CarParkDB"
    )
    print("Connection successful")
except Exception as e:
    print("Unable to connect ", e)

now = datetime.now()
# later = now + timedelta(hours=32, minutes=0)
#
# # dd/mm/YY H:M:S
# dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
# later_string = later.strftime("%d/%m/%Y %H:%M:%S")
#
# diff = later - now
# print("diff =", diff)
#
# days = int(diff.days)
# print(days)
# hours = int(diff.seconds // (60 * 60))
# print(hours)
# # mins = int((diff.seconds // 60) % 60)
# # print(mins)
#
# # read the number from outbound cam and calculate the price
# new_price = days * 100 + hours * 6

# new_plate = input('New Car: ')
# plate_exists = Car.objects(plate_number=new_plate)
# print(plate_exists.first())
#
# if plate_exists.first() is None:
#     enter_car = Car(
#         plate_number=new_plate,
#         enter=now,
#         price=0
#     )
#     enter_car.save()  # This will perform an insert
# else:
#     Car.objects(plate_number=new_plate).update(exit=now, price=new_price)

cars_inside = Car.objects()
for item in cars_inside:
    listbox.insert(END, item.plate_number)


def get_data(custom_filter):
    listbox.delete(0, 'end')
    temp = 'All'
    if custom_filter == 'In':
        temp = Car.objects(price=0)
    elif custom_filter == 'Out':
        temp = Car.objects(price__gt=0)
    else:
        coltbox.current(0)
        temp = Car.objects()
    count_label.configure(text=temp.count())
    for itemm in temp:
        listbox.insert(END, itemm.plate_number)
    # root.after(50000, get_data)


# Callback to show focus change
def updateDisplay(*args):
    value = listbox.curselection()
    selection = listbox.get(value)
    retrieved = Car.objects(plate_number=selection).first()
    global enter_date
    enter_date = retrieved.enter
    global _plate
    _plate = selection
    ll_res.configure(text=selection)
    enl_res.configure(text=retrieved.enter)
    if retrieved.exit is not None:
        exl_res.configure(text=retrieved.exit)
    else:
        exl_res.configure(text="None")
    pl_res.configure(text=retrieved.price)
    cal_btn.configure(state='normal')


def comboSelected(self, event=None):
    print(n.get())
    root.after(500, get_data(n.get()))


listbox.bind('<<ListboxSelect>>', updateDisplay)
coltbox.bind('<<ComboboxSelected>>', comboSelected)
root.mainloop()
