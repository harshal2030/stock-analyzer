import pandas as pd
from matplotlib.figure import Figure
import numpy as np
import datetime
from datetime import timedelta
import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import Formatter
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox as msg
from tkinter import Menu
from tkinter import filedialog as fd
import os
from matplotlib import style
import itertools
#=changes to be made
class MyFormatter(Formatter):
        def __init__(self, dates, fmt='%d-%m-%Y'):
            self.dates = dates
            self.fmt = fmt

        def __call__(self, x, pos=0):
            'Return the label for time x at position pos'
            ind = int(np.round(x))
            if ind >= len(self.dates) or ind < 0:
                return ''

            return self.dates[ind].strftime(self.fmt)

matplotlib.rcParams['backend']='TKAgg'
matplotlib.rcParams.update({'font.size':7})
style.use('ggplot')
#directory file handling
directory='C:/Users/'+os.getlogin()+'/Documents/Stock Data'
if not os.path.exists(directory):
    os.mkdir(directory)

user_data=[]
if os.path.exists(directory+'/user_data.txt'):
    for line in open(directory+'/user_data.txt'):
        for text in line.split(':'):
            text=text.replace('\n', '')
            user_data.append(text)
else:
    rel=open(directory+'/user_data.txt', 'w')
    rel.write('')
user_data=dict(itertools.zip_longest(*[iter(user_data)]*2, fillvalue=''))

files_in_dir=[]
for root, dir, files in os.walk(directory):
    for file in files:
        if file.endswith('.xls'):
            files_in_dir.append(file)
if files_in_dir==[] or '' or None:
    data_to_plot=[]
    date_to_plot=[]
    x=[]
    data={'Symbol': '', 'Expiry Date': '', 'Closing Price': ''}
    data=pd.DataFrame(data, index=[0])
else:
    sort_file=[]
    for i in files_in_dir:
        i=i.replace('.xls', '')
        sort_file.append(i)

    sort_file=sorted(sort_file, key=lambda x: datetime.datetime.strptime(x, '%d-%m-%Y'))
    for a in sort_file[:-1]:
        os.remove(directory+'/'+a+'.xls')
    data=pd.read_excel(directory+'/'+str(sort_file[-1])+'.xls')
    
    #data updation
    recent_datapoint=datetime.datetime.strptime(user_data['date'], '%d-%m-%Y')
    date_data=datetime.datetime.today()
    if recent_datapoint==date_data:
        pass
    else:
        data_date_str=[]
        data_delta=date_data-recent_datapoint
        for i in range(data_delta.days+1):
            d=recent_datapoint+timedelta(i)
            data_date_str.append(d.strftime('%m-%d-%Y'))
        l2=[data]
        for i in data_date_str:
            url='http://www.ncdex.com/Downloads/Bhavcopy_Summary_File/Export_csv/'+i+'.csv'
            url2='http://www.ncdex.com/Downloads/Bhavcopy_Summary_File/doc/'+i+'.xls'
            try:
                dat=pd.read_csv(url, parse_dates=['Expiry Date'])
            except Exception:
                try:
                    dat=pd.read_excel(url2, parse_dates=['Expiry Date'])
                except:
                    pass
            else:
                dat['Date']=datetime.datetime.strptime(i, '%m-%d-%Y')
                l2.append(dat)
        data=pd.concat(l2, axis=0, ignore_index=True)
    data.drop_duplicates(inplace=True)
    data.sort_values(by='Date')
    data=data.loc[:, ~data.columns.str.contains('^Unnamed')]
    data.to_excel(directory+'/'+date_data.strftime('%d-%m-%Y')+'.xls')
    #data updation completed

    data_to_plot=data.loc[(data['Symbol']==user_data['stock']) & (data['Expiry Date']==datetime.datetime.strptime(user_data['expiry'], '%d-%m-%Y')), 'Closing Price']
    date_to_plot=data.loc[(data['Symbol']==user_data['stock']) & (data['Expiry Date']==datetime.datetime.strptime(user_data['expiry'], '%d-%m-%Y')), 'Date']
    x=np.arange(len(date_to_plot))


win=tk.Tk()
fig=Figure(figsize=(6, 5), dpi=100)
ax=fig.add_subplot(111)
font=FontProperties(weight='bold')
hs, =ax.plot(x, data_to_plot, marker='.')
ann=ax.annotate('', xy=(0, 0))
ann_list=[]#annotation address
for x, y in zip(np.arange(len(data_to_plot)), data_to_plot):
    ann=ax.annotate(str(y), xy=(x, y))
    ann_list.append(ann)

if files_in_dir==[] or '' or None:
    pass
else:
    form=MyFormatter(list(date_to_plot))
    ax.xaxis.set_major_formatter(form)
#main interface
win.geometry("{0}x{1}+0+0".format(win.winfo_screenwidth(), win.winfo_screenheight()))

if not user_data=={}:
    fig.suptitle(user_data['stock'], fontsize=15)
#main frames########################################
chart_frame=tk.Frame(win)                          #
widget_frame=tk.Frame(win, bg='white')             #
#notes                                             #
#grid system only                                  #
#defination over####################################
widget_frame.pack(side='top', fill=tk.BOTH)
chart_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)

#stock frame
stock_frame=tk.Frame(widget_frame, bg='white')
stock_frame.grid(column=2, row=0)
stock=tk.StringVar()
label3=ttk.Label(stock_frame, text='Stock:')
label3.pack()
stck_select=ttk.Combobox(stock_frame, width=12, textvariable=stock, state='readonly')
stck_select.pack(padx=0, pady=0)

#expiry frame
exp_frame=tk.Frame(widget_frame, bg='white')
exp_frame.grid(column=3, row=0)
label2=ttk.Label(exp_frame, text='Expiry date:')
label2.pack()
exp_date=tk.StringVar()
exp_selection=ttk.Combobox(exp_frame, width=12, textvariable=exp_date, state='readonly')
exp_selection.pack()

#price frame
data_frame=tk.Frame(widget_frame)
data_frame.grid(column=5, row=0)
data_label=tk.Label(data_frame)
data_label.pack(fill=tk.BOTH, expand=True)
#refinig functions
stc=data.loc[data['Symbol'].notnull(), 'Symbol']
stck_lst=list(set(list(stc)))
stck_select['values']=sorted(stck_lst)

def redefine_exp(event):
    daef=data.loc[(data['Expiry Date'].notnull())&(data.Symbol==stck_select.get()), 'Expiry Date']
    exp_lst=list(set(list(daef)))
    exp_lst.sort()
    exp_lst=[i.strftime('%d-%m-%Y') for i in exp_lst]
    exp_selection['values']=exp_lst

stck_select.bind("<<ComboboxSelected>>", redefine_exp)

def draw_on_click():
    for anot in ann_list:
        try:
            anot.remove()
        except:
            continue
    expi=exp_selection.get()
    stck=stck_select.get()
    if ((expi=='' or None) or (stck=='' or None)):
        msg.showwarning('Warning!', "Not all values were entered! Please enter all values to analyze your selected stock.")
    else:
        expi=datetime.datetime.strptime(expi, '%d-%m-%Y')
        #expi=expi.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
        local=data.loc[(data.Symbol==stck)&(data['Expiry Date']==expi), 'Closing Price']
        #print(data.loc[(data.Symbol==stck)&(data['Expiry Date']==expi), ['Closing Price', 'Date']])
        date_to_=data.loc[(data['Symbol']==stck_select.get()) & (data['Expiry Date']==expi), 'Date']
        ax.set_autoscale_on(True) 
        x=np.arange(len(date_to_))
        hs.set_data(x, local)
        for i, j in zip(x, local):
            ann=ax.annotate(str(j), xy=(i, j))
            ann_list.append(ann)
        form=MyFormatter(list(date_to_plot))
        ax.xaxis.set_major_formatter(form)
        fig.suptitle(stck_select.get(), fontsize=15)
        ax.relim()
        ax.autoscale_view(True, True, True)
        form=MyFormatter(list(date_to_))
        ax.xaxis.set_major_formatter(form)
        fig.canvas.draw()
        def mat_event(e):
            if stck_select.get()!='' and exp_selection!='':
                i=int(round(e.xdata))
                l=list(date_to_)
                t=l[i]
                date_=data.loc[(data['Symbol']==stck_select.get()) & (data['Expiry Date']==datetime.datetime.strptime(exp_selection.get(), '%d-%m-%Y')) & (data['Date']==t), ['Date', 'Opening Price', 'High Price', 'Low Price', 'Closing Price']]
                date_['Date']=date_['Date'].dt.strftime('%d-%m-%Y')#
                date_=date_.to_string()
                date_index=str(data.index[(data['Symbol']==stck_select.get()) & (data['Expiry Date']==datetime.datetime.strptime(exp_selection.get(), '%d-%m-%Y')) & (data['Date']==t)].values.tolist()[0])
                date_=date_.replace(date_index, '')
                data_label.config(text=date_)
        cd=fig.canvas.mpl_connect('motion_notify_event', mat_event)

#button frame
butt_frame=tk.Frame(widget_frame, bg='white')
butt_frame.grid(column=4, row=0)
button=ttk.Button(butt_frame, text='Submit', command=draw_on_click)
button.grid(column=0, row=1)

def new_import():
    folder=fd.askdirectory()
    fls=[]
    for root, dirs, fle in os.walk(folder):
        for files in fle:
            if files.endswith('.csv'):
                fls.append(files)
    if fls==[] or None:
        msg.showerror('Error', 'No csv files found in current directory')
    else:
        df_mcx=[]
        for data in fls:
            mcx=pd.read_csv(folder+'/'+data)
            if list(mcx.columns.values)[0]=='Date':
                df_mcx.append(mcx)
            else:
                mcx=pd.read_csv(folder+'/'+data, sep='\t',parse_dates=['Expiry Date'])
                df_mcx.append(mcx)
        df_mcx=pd.concat(df_mcx, axis=0, ignore_index=True, sort=False)
        df_mcx['Expiry Date']=pd.to_datetime(df_mcx['Expiry Date'])
        df_mcx['Date']=pd.to_datetime(df_mcx['Date'])
        df_mcx.sort_values(by='Date', ascending=True, inplace=True)
        root=tk.Toplevel(win)
        figm=Figure(figsize=(6, 5), dpi=100)
        axm=figm.add_subplot(111)
        hsm, =axm.plot([], [],marker='.')
        annm=axm.annotate('', xy=(0, 0))
        ann_listm=[]#annotation address
        #frames
        chart_frame_mcx=tk.Frame(root)
        widget_frame_mcx=tk.Frame(root, bg='white')
        #ends
        chart_frame_mcx.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=6, pady=6)
        widget_frame_mcx.pack(side=tk.TOP, fill=tk.BOTH)

        #functioning widget
        stock_frame_mcx=tk.Frame(widget_frame_mcx, bg='white')
        stock_frame_mcx.grid(column=2, row=0)
        stock_mcx=tk.StringVar(root)
        labelm1=ttk.Label(stock_frame_mcx, text='Stock:')
        labelm1.pack()
        stck_select_mcx=ttk.Combobox(stock_frame_mcx, width=12, textvariable=stock_mcx, state='readonly')
        stck_select_mcx.pack(padx=1, pady=0)
        stc_mcx=df_mcx.loc[(df_mcx['Symbol'].notnull())&(df_mcx['Instrument Name']=='FUTCOM'), 'Symbol']
        stck_lst_mcx=list(set(list(stc_mcx)))
        stck_select_mcx['values']=sorted(stck_lst_mcx)


        #expiry frame
        exp_frame_mcx=tk.Frame(widget_frame_mcx, bg='white')
        exp_frame_mcx.grid(column=3, row=0)
        labelm2=ttk.Label(exp_frame_mcx, text='Expiry date:')
        labelm2.pack()
        exp_date_mcx=tk.StringVar(root)
        exp_selection_mcx=ttk.Combobox(exp_frame_mcx, width=12, textvariable=exp_date_mcx, state='readonly')
        exp_selection_mcx.pack()

        def redefine_exp_mcx(event):
            daef_mcx=df_mcx.loc[(df_mcx['Expiry Date'].notnull())&(df_mcx.Symbol==stck_select_mcx.get())&(df_mcx['Instrument Name']=='FUTCOM'), 'Expiry Date']
            exp_lst_mcx=list(set(list(daef_mcx)))
            exp_lst_mcx.sort()
            exp_lst_mcx=[i.strftime('%d-%m-%Y') for i in exp_lst_mcx]
            exp_selection_mcx['values']=exp_lst_mcx
        
        stck_select_mcx.bind("<<ComboboxSelected>>", redefine_exp_mcx)

        def draw_on_click_mcx():
            for anot in ann_listm:
                try:
                    anot.remove()
                except:
                    pass
            expi_mcx=exp_selection_mcx.get()
            stck_mcx=stck_select_mcx.get()
            if ((expi_mcx=='' or None) or (stck_mcx=='' or None)):
                msg.showwarning('Warning!', "Not all values were entered! Please enter all values to analyze your selected stock.")
            else:
                expi_mcx=datetime.datetime.strptime(expi_mcx, '%d-%m-%Y')
                #expi=expi.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
                localm=df_mcx.loc[(df_mcx.Symbol==stck_mcx)&(df_mcx['Expiry Date']==expi_mcx)&(df_mcx['Instrument Name']=='FUTCOM'), 'Close']
                localm2=df_mcx.loc[(df_mcx.Symbol==stck_mcx)&(df_mcx['Expiry Date']==expi_mcx)&(df_mcx['Instrument Name']=='FUTCOM'), ['Close', 'Date']]
                print(localm2)
                axm.set_autoscale_on(True)
                xm=np.arange(len(localm))
                hsm.set_data(xm, localm)
                for i, j in zip(xm, localm):
                    annm=axm.annotate(str(j), xy=(i, j))
                    ann_listm.append(annm)
                figm.suptitle(stck_select_mcx.get(), fontsize=15)
                axm.relim()
                axm.autoscale_view(True, True, True)
                figm.canvas.draw()

        butt_frame_mcx=tk.Frame(widget_frame_mcx, bg='white')
        butt_frame_mcx.grid(column=4, row=0)
        button_mcx=ttk.Button(butt_frame_mcx, text='Submit', command=draw_on_click_mcx)
        button_mcx.grid(column=0, row=1)
        
        canvas_mcx=FigureCanvasTkAgg(figm, master=chart_frame_mcx)
        canvas_mcx.draw()
        canvas_mcx.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        figm.subplots_adjust(top=1, bottom=0.04, left=0.04, right=0.99)
        toolbar_mcx=NavigationToolbar2Tk(canvas_mcx, chart_frame_mcx)
        toolbar_mcx.update()
        canvas_mcx._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



#menu bar
menu_bar=Menu(win)#menu bar instance
win.config(menu=menu_bar)#configure main root for adding menu bar
file_menu=Menu(menu_bar, tearoff=0)
new=Menu(file_menu, tearoff=0)
new.add_command(label='Import window', command=new_import)
file_menu.add_cascade(label='New', menu=new)
menu_bar.add_cascade(label='File', menu=file_menu)
#menu bar/

but_var=tk.StringVar(win)

def clicked():    
    #cleaning data process
    date1=cal.get_date()
    date2=datetime.date.today()
    if date1>date2:
        msg.showerror('Error', "An error has ocurred! Please enter suitable date to download data.")
    else:
        dates=[]
        delta=date2-date1
        for i in range(delta.days+1):
            dates.append(date1+timedelta(i))
        date_str=[]
        for i in dates:
            date_str.append(i.strftime('%m-%d-%Y'))
        df=[]
        for date in date_str:
            url='http://www.ncdex.com/Downloads/Bhavcopy_Summary_File/Export_csv/'+date+'.csv'
            url2='https://www.ncdex.com/Downloads/Bhavcopy_Summary_File/doc/'+date+'.xls'
            try:
                data=pd.read_csv(url, parse_dates=['Expiry Date'])
            except Exception:
                try:
                    data=pd.read_excel(url2, parse_dates=['Expiry Date'])
                except:
                    pass
            else:
                data['Date']=date
                df.append(data)
    df=pd.concat(df, axis=0, ignore_index=True)
    df['Date']=pd.to_datetime(df['Date'])
    df=df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df.to_excel(directory+'/'+date2.strftime('%d-%m-%Y')+'.xls')
    #finished cleaning data
    stc=df.loc[df['Symbol'].notnull(), 'Symbol']
    stck_lst=list(set(list(stc)))
    stck_select['values']=sorted(stck_lst)
    stck_select.current(0)
    def get_exp(event):
        daef=df.loc[(df['Expiry Date'].notnull())&(df.Symbol==stck_select.get()), 'Expiry Date']
        exp_lst=list(set(list(daef)))
        exp_lst.sort()
        exp_lst=[i.strftime('%d-%m-%Y') for i in exp_lst]
        exp_selection['values']=exp_lst
    #get expiry date according to stock
    stck_select.bind("<<ComboboxSelected>>", get_exp)

    def _Draw():
        for anot in ann_list:
            try:
                anot.remove()
            except:
                pass
        expi=exp_selection.get()
        stck=stck_select.get()
        if ((expi=='' or None) or (stck=='' or None)):
            msg.showwarning('Warning!', "Not all values were entered! Please enter all values to analyze your selected stock.")
        else:
            expi=datetime.datetime.strptime(expi, '%d-%m-%Y')
            #expi=expi.strftime('%m/%d/%Y').lstrip("0").replace(" 0", " ")
            local=df.loc[(df.Symbol==stck)&(df['Expiry Date']==expi), 'Closing Price']
            date_to=df.loc[(df.Symbol==stck)&(df['Expiry Date']==expi), 'Date']
            date_to_=df.loc[(df['Symbol']==stck) & (df['Expiry Date']==expi), 'Date']
            ax.set_autoscale_on(True)
            x=np.arange(len(date_to))
            hs.set_data(x, local)
            for i, j in zip(x, local):
                ann=ax.annotate(str(j), xy=(i, j))
                ann_list.append(ann)
            fig.suptitle(stck_select.get(), fontsize=15)
            ax.relim()
            ax.autoscale_view(True, True, True)
            form=MyFormatter(list(date_to))
            ax.xaxis.set_major_formatter(form)
            fig.canvas.draw()
            def mpl_event(e):
                if stck_select.get()!='' and exp_selection!='':
                    i=int(round(e.xdata))
                    l=list(date_to_)
                    t=l[i]
                    date_=df.loc[(df['Symbol']==stck_select.get()) & (df['Expiry Date']==datetime.datetime.strptime(exp_selection.get(), '%d-%m-%Y')) & (df['Date']==t), ['Date', 'Opening Price', 'High Price', 'Low Price', 'Closing Price']]
                    date_['Date']=date_['Date'].dt.strftime('%d-%m-%Y')#
                    date_=date_.to_string()
                    date_index=str(df.index[(df['Symbol']==stck_select.get()) & (df['Expiry Date']==datetime.datetime.strptime(exp_selection.get(), '%d-%m-%Y')) & (df['Date']==t)].values.tolist()[0])
                    date_=date_.replace(date_index, '')
                    data_label.config(text=date_)
        cd=fig.canvas.mpl_connect('motion_notify_event', mpl_event)
    button.config(command=_Draw)


date_Frame=tk.Frame(widget_frame, bg='white')
date_Frame.grid(column=0, row=0)
label=ttk.Label(date_Frame, text='Choose Date:')
label.grid(column=0, row=0,padx=0, pady=0)
cal=DateEntry(date_Frame, width=12, background='grey', foreground='white', borderwidth=1)
cal.grid(column=0, row=1,padx=0, pady=0)
date_butt=ttk.Button(date_Frame, text='Get Data', command=clicked)
date_butt.grid(column=1, row=1)

#initialize_tooltip(cal, 'date with date')
def save_onclose():
    if msg.askokcancel("Quit", "Do you want to quit?"):
        hars=exp_selection.get()
        kav=stck_select.get()
        if (hars=='' or kav==''):
            pass
        else:
            data="""date:{0}\nstock:{1}\nexpiry:{2}""".format(datetime.datetime.today().strftime("%d-%m-%Y"), kav, hars)
            file=open(directory+'/user_data.txt', 'w')
            file.write(data)
            file.close()
        win.destroy()

win.protocol("WM_DELETE_WINDOW", save_onclose)


def event(e):
    if (stck_select.get()=='' or None) or (exp_selection.get()=='' or None):
        i=int(round(e.xdata))
        l=list(date_to_plot)
        t=l[i]
        date_=data.loc[(data['Symbol']==user_data['stock']) & (data['Expiry Date']==datetime.datetime.strptime(user_data['expiry'], '%d-%m-%Y')) & (data['Date']==t), ['Date', 'Opening Price', 'High Price', 'Low Price', 'Closing Price']]
        date_['Date']=date_['Date'].dt.strftime('%d-%m-%Y')#
        date_=date_.to_string()
        date_index=str(data.index[(data['Symbol']==user_data['stock']) & (data['Expiry Date']==datetime.datetime.strptime(user_data['expiry'], '%d-%m-%Y')) & (data['Date']==t)].values.tolist()[0])
        date_=date_.replace(date_index, '')
        data_label.config(text=date_)

#end interface
win.title("Stock Analyzer")
win.iconbitmap('gra1.ico')
#chart area
#master: grid
#child: pack
canvas=FigureCanvasTkAgg(fig, master=chart_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

fig.subplots_adjust(top=1, bottom=0.04, left=0.04, right=0.99)

toolbar=NavigationToolbar2Tk(canvas, chart_frame)
toolbar.update()
canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#chart area end

fig.set_canvas(canvas)
cid=fig.canvas.mpl_connect('motion_notify_event', event)
win.mainloop()