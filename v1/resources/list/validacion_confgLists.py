configuracion = {"id_config":{"datatype":str,
                              "requerido":True,
                              "valores_permitidos":[],
                              "valores_prohibidos":[],
                              "valores_unicos":True,
                              "valor_default":None},
                 "first_line_names":{"datatype":bool,
                              "requerido":False,
                              "valores_permitidos":[False, True],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":True},
                 "fields_list":{"datatype":list,
                              "requerido":True,
                              "valor_default":None,
                              "elementos_unicos":True,
                              "datatype_elemento":dict,
                              "config_elemento":{"field_name":{"datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":[],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":True,
                                                               "valor_default":None},
                                                 "datatype":{  "datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":['int','str','bool','date','datetime'],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":'str'},
                                                 "fieldtype":{ "datatype":str,
                                                               "requerido":False,
                                                               "valores_permitidos":['user','phone','other'],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":'other'},
                                                 "config_phone":{"datatype":dict,
                                                                 "requerido":False,
                                                                 "valor_default":{"prefix": "", "digits": -1},
                                                                 "config_elemento":{ "prefix": {"datatype":str,
                                                                                                "requerido":False,
                                                                                                "valores_permitidos":[],
                                                                                                "valores_prohibidos":[],
                                                                                                "valores_unicos":False,
                                                                                                "valor_default":''},
                                                                                     "digits": {"datatype":int,
                                                                                                "requerido":False,
                                                                                                "valores_permitidos":[],
                                                                                                "valores_prohibidos":[1,2,3,4],
                                                                                                "valores_unicos":False,
                                                                                                "valor_default":0}}},
                                                 "skip":{      "datatype":bool,
                                                               "requerido":False,
                                                               "valores_permitidos":[True,False],
                                                               "valores_prohibidos":[],
                                                               "valores_unicos":False,
                                                               "valor_default":False}}},
                 "file_format":{"datatype":str,
                              "requerido":False,
                              "valores_permitidos":['csv','txt'],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":'csv'},
                 "file_codec":{"datatype":str,
                              "requerido":False,
                              "valores_permitidos":[],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":None},                                                
                 "delimiter":{"datatype":str,
                              "requerido":True,
                              "valores_permitidos":[';','.',',',' ','\t'],
                              "valores_prohibidos":[],
                              "valores_unicos":False,
                              "valor_default":';'}
                 }


