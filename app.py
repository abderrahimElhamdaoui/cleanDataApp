import tkinter as tk
from tkinter import *
from tkinter import messagebox,filedialog,ttk,LabelFrame
from tkhtmlview import HTMLLabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os 
import code_data

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        width=1000
        height=500
        self.master.geometry(f"{width}x{height}")
        self.master.title("cleanData")
        self.master.configure(bg='pink')
        my_canvas = Canvas(self.master, width=800, height=500)
        my_canvas.pack(fill="both", expand=True)
        my_canvas.configure(bg='pink')
        my_canvas.create_text(500, 200, text="Welcome!", font=("Helvetica", 50), fill="white") 
        self.create_menu_bar()
        self.file_path=""
        
    def create_menu_bar(self):
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        self.menu_bar.config(bg='#7FFFD4',font= ("serif", 10,"bold"))
        font_menu=("Verdana", 10,"bold")
#         file menu 
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.config(bg='#00BFFF',font=font_menu,fg='white')
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Ovrire", command=self.ovrire_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.destroy)
#         aficher menu
        self.aficher_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.aficher_menu.config(bg='#00BFFF',font=font_menu,fg='white')
        self.menu_bar.add_cascade(label="la lecture des données", menu=self.aficher_menu)
        self.aficher_menu.add_command(label="sous forme de table", command=self.aficher_table)
        self.aficher_menu.add_separator()
        self.aficher_menu.add_command(label="infos sur dataset", command=self.infos_table)
        self.aficher_menu.add_separator()
#         self.aficher_menu.add_command(label="histogrames", command=self.histogrames)
        self.histo_menu = tk.Menu(self.aficher_menu, tearoff=0)
        self.histo_menu.config(bg='#00BFFF',font=font_menu,fg='white')
        self.aficher_menu.add_cascade(label="histogrames", menu=self.histo_menu)
        self.histo_menu.add_command(label="les attributs catégorielles", command=self.histogrames_catVar)
        self.histo_menu.add_separator()
        self.histo_menu.add_command(label="les attributs continues", command=self.histogrames_contVar)
        self.aficher_menu.add_separator()
        self.aficher_menu.add_command(label="Matrice de corrélation", command=self.matriceCorrelation)
#       Nettoyage les données
        self.nettoyage_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.nettoyage_menu.config(bg='#00BFFF',font=font_menu,fg='white')
        self.menu_bar.add_cascade(label="Nettoyage",  menu=self.nettoyage_menu)
        self.nettoyage_menu.add_command(label="Nettoyage", command=self.nettoyage_data)

    def ovrire_file(self):
#         la lecture de dataset avec la suppression les attributs non utiliser.
        self.file_path = filedialog.askopenfilename(title="Select a file",filetypes=[("CSV files", "*.csv")])
        self.data = pd.read_csv(self.file_path)
        colonnes_id = [col for col in self.data.columns if 'id' in col.lower()]
        if len(colonnes_id)!=0:
            self.data.drop([colonnes_id[0]],axis=1,inplace=True)
        print(self.file_path)

    def aficher_table(self):
        self.clear_frame()
        if self.file_path!="":

            self.tree = ttk.Treeview(self.master)
            self.tree["columns"] = tuple(self.data.columns)
#             print(self.data)
            for col in self.data.columns:
                self.tree.heading(col, text=col)

            # Ajouter des données au tree
            for i, row in self.data.iterrows():
                self.tree.insert("", tk.END, values=tuple(row))

            y_scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
            y_scrollbar.pack(side="right", fill="y")
            self.tree.configure(yscroll=y_scrollbar.set)

            x_scrollbar = ttk.Scrollbar(self.master, orient="horizontal", command=self.tree.xview)
            x_scrollbar.pack(side="bottom", fill="x")
            self.tree.configure(xscroll=x_scrollbar.set)
        
            self.tree.pack(expand=True, fill=tk.BOTH)
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant d'afficher la table.")
    
    def infos_table(self):
        if self.file_path!="":            
            self.clear_frame()

            self.labelframe = ttk.Labelframe(self.master, text="Infos sur dataset")
#             self.labelframe = tk.Frame(self.master, padx=20, pady=20)
            self.labelframe.pack(padx=10, pady=10)
    
            style = ttk.Style()
            style.configure('TLabelframe.Label', background='lightblue',foreground ='white',font=('courier', 15, 'bold')) 
            style.configure('TLabelframe', background='lightblue')
            self.labelframe.pack(expand="yes",fill="both")
            
            txtHtml="<html><p style='color:black;background-color: pink;'><b>"
            font_label=('courier', 15, 'bold')
            canva=self.scrollFrame(self.labelframe)

#           récupérer les infos a dataset
            rows ,columns= self.data.shape
            num_variables = list(self.data.select_dtypes(include=['number']).columns)
            cat_variables = list(self.data.select_dtypes(include=['object']).columns) 

            txt="<p>le nombre des lignes est : "+str(rows)+"</p>"
            txtHtml+=txt+"<br>"
           
            txt="<p>le nombre des colonnes est : "+str(columns)+"</p>"
            txtHtml+=txt+"<br>"
            
            txt="<p>les attribute numérique :<span style='color:#000080;'> "+str(num_variables)+"</span></p>"
            txtHtml+=txt+"<br>"
           
            txt="<p>les attribute categorical :<span style='color:#000080;'> "+str(cat_variables)+"</span></p>"
            txtHtml+=txt+"<br>"

            nan_columns = self.data.loc[: ,self.data.isna().sum() != 0].columns
            listeDesnull=[]
            ligTablehtml=""
            for tmp in nan_columns:
                listeDesnull.append([tmp,self.data[tmp].isnull().sum()])
                ligTablehtml+="<tr><td>"+tmp+" : </td><td>"+str(self.data[tmp].isnull().sum())+"</td><tr>"
            
            tableHtaml="<table>"+ligTablehtml+"</table>"
            if len(nan_columns)==0:
                tableHtaml="n'existe un attribut pas qui contient des valeurs manquante"
            txt="<p>les attributs qui contient des valeurs manquante est : "
            txtHtml+=txt+tableHtaml+"</p><br>"
            
            txtHtml+="</b></p></html>"
            html=HTMLLabel(canva,html=txtHtml,width=120,height="100")
            html.pack(fill="both", expand=True,padx=10, pady=10)
            html.config(bg='pink',font=("Verdana", 10,"bold"))
            
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant.")
        
    def histogrames_catVar(self):
        self.clear_frame()
        if self.file_path!="":
            cat_variables = list(self.data.select_dtypes(include=['object']).columns)
            if len(cat_variables)!=0:
                label = Label(self.master, text="les histogrammes des variables catégorielles", font=("Helvetica", 14),bg='white')
                label.pack(pady=10)
    #             tracer les histogrammes des variables catégorielles.
                nbLignes=0
                if len(cat_variables)%2==0:
                    nbLignes=len(cat_variables)//2
                else:
                    nbLignes=(len(cat_variables)//2)+1
        
                fig, axes = plt.subplots(nbLignes, 2, figsize=(10, 20), sharey=True)
                for var, subplot in zip(cat_variables, axes.flatten()):
                    sns.histplot(x=var, data=self.data, ax=subplot)
                    subplot.set_title(f"histogramme pour l'attribut '{var}'")
                    for label in subplot.get_xticklabels():
                        label.set_rotation(45)

                plt.subplots_adjust(bottom=0.2,wspace=0.5, hspace=1.5)
                scroleFrame=self.scrollFrame(self.master)
                canvas = FigureCanvasTkAgg(fig, master=scroleFrame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showerror("cleanData", "n'existe pas des variables catégorielles.")
            
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant.")
    
    def histogrames_contVar(self):
        self.clear_frame()
        if self.file_path!="":
            num_variables = list(self.data.select_dtypes(include=['number']).columns)
            if len(num_variables)!=0:
                
                label = Label(self.master, text="les histogrammes des variables continues", font=("Helvetica", 14),bg='white')
                label.pack(pady=10)
    #             tracer les histogrammes des variables continues.
                nbLignes=0
                if len(num_variables)%2==0:
                    nbLignes=len(num_variables)//2
                else:
                    nbLignes=(len(num_variables)//2)+1
        
                fig, axes = plt.subplots(nbLignes, 2, figsize=(10, 20), sharey=True)
                for var, subplot in zip(num_variables, axes.flatten()):
                    sns.histplot(self.data[var], kde=True, ax=subplot)
                    subplot.set_title(f"histogramme pour l'attribut '{var}'")
                    for label in subplot.get_xticklabels():
                        label.set_rotation(45)

                plt.subplots_adjust(bottom=0.2,wspace=0.5, hspace=1.5)
                scroleFrame=self.scrollFrame(self.master)
                canvas = FigureCanvasTkAgg(fig, master=scroleFrame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            else:
                messagebox.showerror("cleanData", "n'existe pas des variables continues.")
            
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant.")
    
    
    def matriceCorrelation(self):
        self.clear_frame()
        if self.file_path!="":
            data=self.data.select_dtypes(include=['number'])
            if len(data.columns)!=0:
                corr_matrix = data.corr()
                rows, cols = corr_matrix.shape
                label = Label(self.master, text="la matrices de corrélation", font=("Helvetica", 14),bg='cyan',fg='black')
                label.pack(pady=10)
                scrolFrame=self.scrollFrame(self.master)
                scrolFrame.pack()
                scrolFrame.config(bg='red')
                label = ttk.Label(scrolFrame, text=" ",background='black',foreground="white",font=("Helvetica", 10))
                label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
                for j in range(cols):
                    label = ttk.Label(scrolFrame, text=data.columns[j],background='black',foreground="white",font=("Helvetica", 10))
                    label.grid(row=0, column=j+1, padx=10, pady=10, sticky="nsew")
                    label = ttk.Label(scrolFrame, text=data.columns[j],background='black',foreground="white",font=("Helvetica", 10))
                    label.grid(row=j+1, column=0, padx=10, pady=10, sticky="nsew")

                for i in range(rows):
                    for j in range(cols):
                        value = corr_matrix.iloc[i, j]
                        label = ttk.Label(scrolFrame, text=f"{value:.2f}",background='black',foreground="white",font=("Helvetica", 10))
                        label.grid(row=i+1, column=j+1, padx=5, pady=5, sticky="nsew")
            else:
                messagebox.showerror("cleanData", "n'existe pas des variables numérique.")
            
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant.")
    
    def nettoyage_data(self):
        if self.file_path!="":
            self.clear_frame()
            my_canvas = Canvas(self.master, width=800, height=500)
            my_canvas.pack(fill="both", expand=True)
            my_canvas.configure(bg='pink')
            label= Label(my_canvas,text="En traitment ...", font=("Helvetica", 30), bg='pink',fg="white")
            label.pack(padx=10, pady=20)
            messagebox.showinfo("cleanData", "votre dataset en traitement.")
            tmp=code_data.press(self.file_path)
            self.data_netouayer=tmp.data_final()

            label.config(text="bien netouayer!") 
            telButton = Button(my_canvas, command=self.telcharger_data,text="Télécharger", font=("Helvetica", 10),height= 2, width=15,bg='cyan',fg="black")
            telButton.pack()
        else:
            messagebox.showerror("cleanData", "Veuillez sélectionner un fichier avant.")
    
        
    def telcharger_data(self):
        pathDec='telechargement'
        isExist = os.path.exists(pathDec)
        if isExist==False:
            os.mkdir(pathDec)
        head, tail = os.path.split(self.file_path)
        fileTel=self.data_netouayer.to_csv("telechargement/"+tail,index=False)
        messagebox.showinfo("cleanData", "aller à le dossier téléchargement et récupérer votre dataset nettoyer.")
        self.clear_frame()
        self.file_path=""
        
    def clear_frame(self):
        for widget in self.master.winfo_children():
            if not isinstance(widget, tk.Menu):
                widget.destroy()
                
    def scrollFrame(self,root):
        main_frame = Frame(root)
        main_frame.pack(fill=BOTH,expand=1)
        main_frame.config(bg='red')
        sec = Frame(main_frame)
        sec.config(bg='white')
        sec.pack(fill=X,side=BOTTOM)
        my_canvas = Canvas(main_frame)
        my_canvas.pack(side=LEFT,fill=BOTH,expand=1)
        my_canvas.config(bg='pink')
        x_scrollbar = ttk.Scrollbar(sec,orient=HORIZONTAL,command=my_canvas.xview)
        x_scrollbar.pack(side=BOTTOM,fill=X)
        y_scrollbar = ttk.Scrollbar(main_frame,orient=VERTICAL,command=my_canvas.yview)
        y_scrollbar.pack(side=RIGHT,fill=Y)
        my_canvas.configure(xscrollcommand=x_scrollbar.set)
        my_canvas.configure(yscrollcommand=y_scrollbar.set)
        my_canvas.bind("<Configure>",lambda e: my_canvas.config(scrollregion= my_canvas.bbox(ALL))) 
        second_frame = Frame(my_canvas)
        second_frame.config(bg='pink')
        my_canvas.create_window((0,0),window= second_frame, anchor="nw")
        return second_frame
    
myapp = App()
myapp.mainloop()