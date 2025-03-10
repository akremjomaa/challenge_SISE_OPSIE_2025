import pandas as pd

df = pd.read_parquet("log_export.parquet")
gb = df.groupby(by="ipsrc")
tab = pd.DataFrame(index=gb.indices.keys())
tab['nombre'] = gb.size()
tab['cnbipdst'] = gb.nunique()['ipdst']
tab['cnportdst'] = gb.nunique()['portdst']
temp = gb.value_counts(['action']).reset_index()
res = pandas.crosstab(temp['ipsrc'],temp['action'],temp['count'],aggfunc=lambda x:x)
res = res.fillna(0)

tab['Permit'] = res['PERMIT'].astype(int)
tab['adminpermit'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='PERMIT')*(sdf.portdst.isin([21,22,3389,3306]))))
tab['infeq1024permit'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='PERMIT')*(sdf.portdst <= 1024)))
tab['1024-49152permit'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='PERMIT')*(sdf.portdst > 1024)*(sdf.portdst <= 49152)))
tab['sup49152permit'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='PERMIT')*(sdf.portdst > 49152)))


tab['Deny'] = res['DENY'].astype(int)
tab['admindeny'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='DENY')*(sdf.portdst.isin([21,22,3389,3306]))))
tab['infeq1024deny'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='DENY')*(sdf.portdst <= 1024)))
tab['1024-49152deny'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='DENY')*(sdf.portdst > 1024)*(sdf.portdst <= 49152)))
tab['sup49152permit'] = gb.apply(lambda sdf:numpy.sum((sdf.action=='PERMIT')*(sdf.portdst > 49152)))