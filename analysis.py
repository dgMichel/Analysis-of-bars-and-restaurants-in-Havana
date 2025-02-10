#Dependencias utilizadas
import json
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.express as px

data=os.listdir("data") #lista con los nombres de cada json dentro de la carpeta "data"

#Este procedimiento es para añadir todos los json a un SUPER diccionario con toda la información :D 
#iteramos por cada archivo json y los agrupamos en la variable super teniendo en cuenta la estructura {"Municipio":{"nombre del json":"contenido"}}

def Create_super(paths):
    super={}
    for i in paths:
        with open("data/"+i) as json_file:
            x=json.load(json_file) #Abre y carga cada json dentro de la carpeta
            if not(x["general_info"]["township"] in super.keys()): 
                super[x["general_info"]["township"]]={}
                super[x["general_info"]["township"]][x["general_info"]["name"]]=x
            else:
                super[x["general_info"]["township"]][x["general_info"]["name"]]=x
    return super

#Genera un grafico de pastel con el porcentaje de locales con respecto al total
def Locals_Type(paths):
    local={} # almacena el tipo de local en las key y la cantidad en el value
    for i in paths:
        with open("data/"+i) as json_file:
                x=json.load(json_file)
        #identifica si la llave no existe para añadirla y darle valor, en caso contrario suma 1 a la cantidad
        if not(x["general_info"]["local"]) in local.keys():
                local[x["general_info"]["local"]]=1
        else:
                local[x["general_info"]["local"]]+=1

    #genera la figura donde las label son el tipo de local y los valores la frecuencia de los mismos
    fig = make_subplots(1, specs=[[{'type':'domain'}]],
            subplot_titles=['Total:248'])
    fig.add_trace(go.Pie(labels=list(local.keys()), values=list(local.values()), scalegroup='one',textposition="outside",pull=0.1,
            name="Locales"), 1, 1)
    fig.update_layout(title_text='Porciento de Locales')
    return fig


#Genera un grafico de barras con los 3 tipos de locales elegidos para mostrar la cantidad por municipios
def Main_Locals(super,lista):
    values=[] #lista para construir el DataFrame
    for i in super.keys():#itera por municipios
        val=[i,0,0,0] #lista para guardar el nombre del municipios y frecuencia del local en el mismo orden de la lista recibida
        for j in super[i].keys():#itera por json del municipio
            if super[i][j]["general_info"]["local"]==lista[0]: val[1]+=1
            elif super[i][j]["general_info"]["local"]==lista[1]: val[2]+=1
            elif super[i][j]["general_info"]["local"]==lista[2]: val[3]+=1
        values.append(val[:]) 

    data = pd.DataFrame(values, columns=["Municipio",lista[0],lista[1],lista[2]])
    #genera el grafico
    fig = px.bar(data, x="Municipio", y=[lista[0],lista[1],lista[2]], title="Tipos de locales por municipio")
    return fig

#Grafica con el costo promedio por categoria de comida de cada municipio
def Average_cost(super):
    values=[] #lista para construir el DataFrame
    def Promedy(super,township,key): #funcion que calcula el promedio de cada categoria por municipio
        total=0
        for i in super[township].keys(): #se accede a cada json del municipio y se busca la lista de precios de la categoria
            if super[township][i]["food"]["menu"][key][key+"_price"]!=[]: 
                #se suma a la variable total el promedio de los precios para el json en particular         
                total+=sum(super[township][i]["food"]["menu"][key][key+"_price"])//len(super[township][i]["food"]["menu"][key][key+"_price"])
        return total//len(super[township].keys()) #se retorna el total entre la cantidad de json del municipio 

    for i in super.keys():
        val=[i] #lista que guarda el municipio y los promedios de cada categoria
        promedio=0
        for j in super[i].keys():
            for k in super[i][j]["food"]["menu"].keys(): #aqui accedemos a cada categoria de comida del json para llamar a Promedy
                if k=="drinks":
                    pass
                else:
                    promedio+=Promedy(super,i,k,)
                    aux=promedio
                    val.append(aux)
                    promedio=0
            break #usamos el break para romper despues del primer json ya que la funcion Promedy trabaja con todo el municipio
        values.append(val[:])
        #construccion del data frame y figura
    data=pd.DataFrame(values,columns=["Municipio","Entrantes","Guarniciones","Hamburguesas","Panes","Principales","Del Mar","Pasta","Pizza","Agregos","Postres"])
    fig=px.line(data,x="Municipio",y=["Entrantes","Guarniciones","Hamburguesas","Panes","Principales","Del Mar","Pasta","Pizza","Agregos","Postres"])
    return fig        

#funcion que determinara el costo promedio de lo que supondria "desayunar/merendar" y "almorzar/comer" por municipio
def Meals_Average_Cost(super):
    """A continuacion presentamos 5 listos que serian nuestra interpretacion sobre que significa
    desayunar/merendar o comer/almorzar en un restaurante. Como abstraccion se referira a la primera
    opcion elegir al menos un aperitivo/pan/hamburguesa y una bebida y para la segunda opcion comer 
    significaria elegir al menos un aperitivo/guarnicion, un plato fuerte(pasta, pizza, maritimo o terreste),
    un postre y una bebida. Por ello designamos 5 listas que englobaran estas variantes individuales
    """
    breakfast=["appetizers","bread","hamburger"]
    drinks=["alcohol","infusions","non_alcoholic"]
    starters=["appetizers","garnishes"]
    main=["main","sea_food","pasta","pizza"]
    dessert=["dessert"]
    values=[] #variable para crear el DataFrame
    def Promedy(lista,municipio,restaurante): #Funcion que calculara el promedio de elegir una de las listas antes mencionadas para un restaurante en especifico
        suma=0
        count=0
        if lista==["alcohol","infusions","non_alcoholic"]:#hacemos una diferenciacion especial para el caso de las bebidas por tener diferente estructura
            for k in lista:
                if super[municipio][restaurante]["food"]["menu"]["drinks"][k+"_price"]!=[]:
                    for l in super[municipio][restaurante]["food"]["menu"]["drinks"][k+"_price"]:
                        suma+=l
                        count+=1
        else:
            for k in lista:
                if super[municipio][restaurante]["food"]["menu"][k][k+"_price"]!=[]:
                        for l in super[municipio][restaurante]["food"]["menu"][k][k+"_price"]:
                            suma+=l
                            count+=1
        return [suma,count] #el resultado es una lista que contendra la suma de todos los valores de los platos de cada lista con la cantidad de platos
    for i in super.keys():
        val=[i,0,0] #almacena el municipio, el promedio del "desayuno" y el promedio de la "comida"
        tuple_1=[0,0] #lista para almacenar la suma y cuenta parcial de cada restaurante para el desayuno
        tuple_2=[0,0] #lista para almacenar la suma y cuenta parcial de cada restaurante para la comida
        for j in super[i].keys():
            for h in range(2): #iteramos por cada restaurante y guardamos la suma total y cantidad total de los promedios en las respectivas listas
                tuple_1[h]+=Promedy(breakfast,i,j)[h]+Promedy(drinks,i,j)[h]
                tuple_2[h]+=Promedy(starters,i,j)[h]+Promedy(main,i,j)[h]+Promedy(dessert,i,j)[h]
        val[1]=tuple_1[0]//tuple_1[1]
        val[2]=tuple_2[0]//tuple_2[1] #asignamos a val el promedio de cada combinacion por municipio
        values.append(val[:])

    data=pd.DataFrame(values,columns=["Municipios","desayunos y meriendas","almuerzos y comidas"])
    fig=px.line(data,x="Municipios",y=["desayunos y meriendas","almuerzos y comidas"])
    return fig

#esta funcion devolvera la variedad de comidas y bebidas por restaurantes de los 3 municipios elegidos
#Playa, Centro Habana y Habana del Este
def Item_Diversity(super):
    municipios=["Habana del Este","Centro Habana","Playa"]
    figures=[] #lista que almacenara las figuras de cada municipio siguiendo orden de comida,bebida
    for i in municipios:
        values_food=[]
        values_drink=[]
        for j in super[i].keys():
            val_food=[j,0]
            val_drink=[j,0]
            for k in super[i][j]["food"]["menu"].keys():
                if k=="drinks":
                    val_drink[1]+=len(super[i][j]["food"]["menu"]["drinks"]["alcohol_list"])+len(super[i][j]["food"]["menu"]["drinks"]["infusions_list"])+len(super[i][j]["food"]["menu"]["drinks"]["non_alcoholic_list"])
                else:
                    val_food[1]+=len(super[i][j]["food"]["menu"][k][k+"_list"])
            values_food.append(val_food[:])
            values_drink.append(val_drink[:])
        data_food=pd.DataFrame(values_food,columns=[i,"comidas"])
        data_drink=pd.DataFrame(values_drink,columns=[i,"bebidas"])
        fig1=px.bar(data_food,x=i,y="comidas")
        fig2=px.bar(data_drink,x=i,y="bebidas")
        figures.append(fig1)
        figures.append(fig2)
    return figures

