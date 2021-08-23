# dev : comparison file1
# prod : comparison file2
# dev_path : comparison file1 path
# prod_path : comparison file2 path
# matchingcols : Common column to compare on
# ignore_columns : Columns to not compare
# comparison_columns ; Columns to compare
# out_path : Output path

if __name__ = '__main__':
    comparison_creator(dev_path,prod_path,matchingcols,ignore_columns,comparison_columns,out_path)

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def checker(x,color_code):
    output = []
    color = 'red'
    keyauth = 1
    for index, row in x.iterrows():

        for col in x.columns:
            keyauth = 0
            for rex in color_code:
                if all([index == rex['index'],any([col in [rex['column']+'_DEV',rex['column']+'_PROD']])]):
                    output.append("background: red")
                    keyauth =1
                    break
            if keyauth == 0:
                output.append("")
    l,b = x.shape
    return chunkIt(output,l)

def color(val):
    if val != '':
        color = 'background-color: red'
    else:
        color = ''
    return  color
    
def comparison_creator(dev_path,prod_path,matchingcols,ignore_columns,comparison_columns,out_path):
    
    import pandas as pd
    import xlwt
    import xlsxwriter
    
    headers = comparison_columns+ignore_columns

    dev = pd.read_csv(dev_path)
    prod = pd.read_csv(prod_path)

    # Data cleaning :
    dev = dev[headers].drop(columns =ignore_columns)
    prod = prod[headers].drop(columns =ignore_columns)
    
    outunique = pd.concat([dev[matchingcols].reset_index(drop=True),prod[matchingcols].reset_index(drop=True)],ignore_index='True').drop_duplicates()
    comparor_list = [x  for x in headers if x not in matchingcols+ignore_columns]
    output = pd.DataFrame(columns=[matchingcols+comparor_list])

    # Key_creation
    data = [dev,prod,outunique,output]
    for fr in data:
        fr['Key'] = fr[matchingcols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    out = pd.DataFrame()
    dev.columns = [str(col) + '_DEV'  if col!= "Key" else "Key" for col in dev.columns ]
    prod.columns = [str(col) + '_PROD' if col!= "Key" else "Key" for col in list(prod.columns) ]

#   Merger
    for index, row in outunique.iterrows():

        dev_part = dev[dev['Key']==outunique['Key'][index]]
        prod_part = prod[prod['Key'] == outunique['Key'][index]]
        record = pd.merge(dev_part,prod_part,on="Key",how="outer")
        out = pd.concat([out,record], ignore_index=True)
    out = out[[str(x) + '_DEV' for x in comparison_columns]+[x+'_PROD' for x in comparison_columns]]
    out = out.reindex(sorted(out.columns), axis=1)
    
#   Compaison Color code creator
    color_code = []
    for index, row in out.iterrows():
        for x in comparison_columns:
            if str(row[str(x)+'_DEV'])!=str(row[str(x)+'_PROD']):
                color_code.append({'column':x,'index':index,'prod_val':row[x+'_PROD'],'dev_val':row[str(x) + '_DEV']})

    color_tag = checker(out,color_code)
    df = pd.DataFrame(color_tag)



    tagged_color = df.style.applymap(color)
    
    writer = pd.ExcelWriter(out_path+r'\DEV_PROD_Comparison.xlsx',engine='xlsxwriter')

    out.to_excel(writer,sheet_name='Comparor',engine='xlsxwriter', index=False)
    tagged_color.to_excel(writer,sheet_name='Color_Code',engine='xlsxwriter', index=False)
    print(color_code)
    if color_code != []:
        pd.DataFrame(color_code).sort_values(by=['column']).to_excel(writer,sheet_name='Mismatch',engine='xlsxwriter', index=False)
    writer.save()
