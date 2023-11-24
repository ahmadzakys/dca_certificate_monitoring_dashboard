######-----Import Dash-----#####
import dash
from dash import dcc
from dash import html, callback, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

from datetime import date
from dateutil.relativedelta import relativedelta

import plotly.graph_objects as go

dash.register_page(__name__, path='/', name='Summary') # '/' is home page

##-----page 1

## -----LAYOUT-----
layout = html.Div([
                html.Br(),
                        html.P(children=html.Strong('MONITORING CERTIFICATE'), 
                               style={'textAlign': 'center', 'fontSize': 27, 'background-color':'#F1F4F4','color':'#242947','font-family':'Verdana'}),
                dbc.Row([
                    html.Div(dash_table.DataTable(
                        id="data_dashboard",
                        columns=[{'name':['VESSEL','TYPE'],'id': 'level_0'},
                                 {'name':['VESSEL','VESSEL NAME'],'id': 'NAMA KAPAL'},
                                 {'name':['CLASS SURVEY','NAT & TONNAGE'],'id': 'NATIONALITY & TONNAGE'},
                                 {'name':['CLASS SURVEY','SOLAS'],'id': 'SOLAS'},
                                 {'name':['CLASS SURVEY','POLLUTION'],'id': 'POLLUTION'},
                                 {'name':['CLASS SURVEY','CLASS'],'id': 'CLASS'},
                                 {'name':['CLASS SURVEY','INSURANCE'],'id': 'INSURANCE'},
                                 {'name':['CLASS SURVEY','LSA & FFA'],'id': 'LSA & FFA'},
                                 {'name':['CLASS SURVEY','HEALTH'],'id': 'HEALTH'},
                                 {'name':['CLASS SURVEY','OTHERS'],'id': 'OTHERS'},],
                        merge_duplicate_headers=True,
                        # style_as_list_view=True,
                        style_header={'backgroundColor': '#2a3f5f',
                                    'fontWeight': 'bold',
                                    'color':'white',
                                    'border': '1px solid white'
                                },
                        style_cell_conditional=[{'if': {'column_id': 'NAMA KAPAL'},
                                                'width': '19%'},
                                                {'if': {'column_id': 'level_0'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'NATIONALITY & TONNAGE'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'SOLAS'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'POLLUTION'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'CLASS'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'INSURANCE'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'LSA & FFA'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'HEALTH'},
                                                'width': '9%'},
                                                {'if': {'column_id': 'OTHERS'},
                                                'width': '9%'},
                                                {'textAlign': 'center'}
                                                ],
                        style_cell={'font-family':'Verdana',
                                    'fontSize': 15,
                                    'color':'#2a3f5f'},
                        style_data_conditional=(
                            [
                                {'if': {'filter_query': '{{{col}}} eq "✔️"'.format(col=col),
                                        'column_id': col},
                                'backgroundColor': '#dfd'} for col in ['NATIONALITY & TONNAGE','SOLAS','POLLUTION','CLASS','INSURANCE','LSA & FFA','HEALTH', 'OTHERS']
                            ] +
                            [
                                {'if': {'filter_query': '{{{col}}} eq "🔲"'.format(col=col),
                                        'column_id': col},
                                'backgroundColor': '#dfd'} for col in ['NATIONALITY & TONNAGE','SOLAS','POLLUTION','CLASS','INSURANCE','LSA & FFA','HEALTH', 'OTHERS']
                            ] +
                            [
                                {'if': {'filter_query': '{{{col}}} eq "⚠️"'.format(col=col),
                                        'column_id': col},
                                'backgroundColor': '#ffd'} for col in ['NATIONALITY & TONNAGE','SOLAS','POLLUTION','CLASS','INSURANCE','LSA & FFA','HEALTH', 'OTHERS']
                            ] +
                            [
                                {'if': {'filter_query': '{{{col}}} eq "❌"'.format(col=col),
                                        'column_id': col},
                                'backgroundColor': '#fdd'} for col in ['NATIONALITY & TONNAGE','SOLAS','POLLUTION','CLASS','INSURANCE','LSA & FFA','HEALTH', 'OTHERS']
                            ] +
                            [
                                {'if': {'column_id': 'level_0',},
                                'fontWeight': 'bold'},
                                {'if': {'filter_query': '{level_0} eq "Tugboat" || {level_0} eq "CTS"',
                                        'column_id': ['level_0']},
                                'backgroundColor': '#F8F6F0'},    
                            ]),
                        css=[{
                            'selector': '.dash-table-tooltip',
                            'rule': 'background-color: white; font-family: Verdana; font-size: 10; color: #2a3f5f;'}],
                        tooltip_delay=0,
                        tooltip_duration=None
                    ))
                ]),

    html.Br(),
    html.Footer('DCA',
            style={'textAlign': 'center', 
                'fontSize': 20, 
                'background-color':'#2a3f5f',
                'color':'white'})
    ], style={
        'paddingLeft':'10px',
        'paddingRight':'10px',
    })

#### Callback Auto Update Chart & Data
@callback(
    [
    Output('data_dashboard', 'data'),
    # Output('data_dashboard', 'tooltip_data'),
    ],
    Input('store', 'data')
)
def update_charts(data):
    ######################
    # Pre Processing
    ######################
    # Tug Boat
    ######################
    df_tb = pd.DataFrame(data['Tugboat'])

    ### datetime variable
    col = df_tb.columns
    col = list(col)

    no_date = ['NO', 'NAMA KAPAL', 'YEARD OF BUILD', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)', 
            '3/6/12 BULAN', ]
    col = [x for x in col if x not in no_date]

    ### apply datetime to selected variable
    df_tb = df_tb.replace(r'^\s*$', np.nan, regex=True)
    df_tb[col] = df_tb[col].apply(pd.to_datetime, format='%d %B %Y')

    ### remove unnecessary variable
    col_del = ['NO', 'YEARD OF BUILD', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)',
            '3/6/12 BULAN', 'NOTA DINAS 1', 'NOTA DINAS 2']
    col_stay = [x for x in df_tb.columns if x not in col_del]

    ### set 'NAMA KAPAL' as index
    df_tb = df_tb[col_stay].set_index('NAMA KAPAL')

    ### making new dataframe for remaining days only
    df_tb_days = df_tb.copy()
    for i in df_tb:
        df_tb_days[i] = (df_tb[i]-pd.to_datetime('today')).dt.days

    ### making new columns(Others) based on the minimum of 4 variables
    df_tb_days['Others'] = df_tb_days[['SERTIFIKAT NASIONAL SISTEM ANTI TERITIP (CERTIFICATE FOULING SISTEM)',
                                    'DOKUMEN PENGAWAKAN MINIMUM (MINIMUM SAFE MANNING DOCUMENT)',
                                    'SERTIFIKAT SIKR (SURAT IZIN STASIUN RADIO KAPAL LAUT)',
                                    'IJIN PENGOPERASIAN KAPAL DALAM NEGERI (RPT) (DOMESTIC VESSEL OPERATING PERMIT)']].min(axis=1)

    ### making new dataframe for status with emoji using df_tb_days
    df_tb_status = df_tb_days.copy()
    for i in df_tb_days:
        df_tb_status[i] = df_tb_status[i].apply(lambda x:
                                                '❌' if x < 0 else (
                                                    '⚠️' if x < 30 else(
                                                        '🔲' if pd.isna(x) else '✔️')))
    
    ######################
    # Barge
    ######################
    df_ba = pd.DataFrame(data['Barge'])

    ### datetime variable
    col_ba = df_ba.columns

    col_ba = list(col_ba)

    no_date = ['NO', 'NAMA KAPAL', 'YEARD OF BUILD', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)', 
            '3/6/12 BULAN', ]
    col_ba = [x for x in col_ba if x not in no_date]

    ### apply datetime to selected variable
    df_ba = df_ba.replace(r'^\s*$', np.nan, regex=True)
    df_ba[col_ba] = df_ba[col_ba].apply(pd.to_datetime, format='%d %B %Y')

    ### remove unnecessary variable
    col_del_ba = ['NO', 'YEARD OF BUILD', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)',
                  '3/6/12 BULAN', 'NOTA DINAS 1', 'NOTA DINAS 2']
    col_stay_ba = [x for x in df_ba.columns if x not in col_del_ba]

    ### set 'NAMA KAPAL' as index
    df_ba = df_ba[col_stay_ba].set_index('NAMA KAPAL')

    ### making new dataframe for remaining days only
    df_ba_days = df_ba.copy()
    for i in df_ba:
        df_ba_days[i] = (df_ba[i]-pd.to_datetime('today')).dt.days

    ### making new columns(Others) based on the minimum of 4 variables
    df_ba_days['Others'] = df_ba_days[['SERTIFIKAT NASIONAL SISTEM ANTI TERITIP (CERTIFICATE FOULING SYSTEM)',
                                    'IJIN PENGOPERASIAN KAPAL DALAM NEGERI (RPT) (DOMESTIC VESSEL OPERATING PERMIT)']].min(axis=1)

    ### making new dataframe for status with emoji using df_tb_days
    df_ba_status = df_ba_days.copy()
    for i in df_ba_days:
        df_ba_status[i] = df_ba_status[i].apply(lambda x:
                                                '❌' if x < 0 else (
                                                    '⚠️' if x < 30 else(
                                                        '🔲' if pd.isna(x) else '✔️')))
    
    ######################
    # CTS
    ######################
    df_cts = pd.DataFrame(data['CTS'])

    ### datetime variable
    col = df_cts.columns
    col = list(col)

    no_date_cts = ['NO', 'NAMA KAPAL', 'YEARD OF BUILD', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)', 
            '3/6/12 BULAN', ]
    col = [x for x in col if x not in no_date_cts]

    ### apply datetime to selected variable
    df_cts = df_cts.replace(r'^\s*$', np.nan, regex=True)
    df_cts[col] = df_cts[col].apply(pd.to_datetime, format='%d %B %Y')

    ### remove unnecessary variable
    col_del_cts = ['NO','INTERMEDATE SURVEY','SPESIAL SURVEY',"INTERMEDATE SURVEY2",'SPESIAL SURVEY2','INTERMEDATE SURVEY3',
            'SPESIAL SURVEY3', 'SURAT UKUR INTERNATIONAL (INTERNATIONAL TONNAGE CERTIFICATE)',
            '3/6/12 BULAN', 'NEXT RENEWAL SYABANDAR','NOTA DINAS 1', 'NOTA DINAS 2',
            'NEXT ANNUAL', 'REMOVAL OF WRECKS1', 'HULL & MACHINE', 'CERTIFIACATE DOCUMENT OF COMPLAINCE', ]
    col_stay_cts = [x for x in df_cts.columns if x not in col_del_cts]

    ### set 'NAMA KAPAL' as index
    df_cts = df_cts[col_stay_cts].set_index('NAMA KAPAL')

    ### making new dataframe for remaining days only
    df_cts_days = df_cts.copy()
    for i in df_cts:
        df_cts_days[i] = (df_cts[i]-pd.to_datetime('today')).dt.days

    ### making new columns(Others) based on the minimum of 4 variables
    df_cts_days['Others'] = df_cts_days[['SERTIFIKAT NASIONAL SISTEM ANTI TERITIP (CERTIFICATE FOULING SISTEM)',
                                        'DOKUMEN PENGAWAKAN MINIMUM (MINIMUM SAFE MANNING DOCUMENT)',
                                        # 'SERTIFIKAT SIKR (SURAT IZIN STASIUN RADIO KAPAL LAUT)',
                                        # 'IJIN PENGOPERASIAN KAPAL DALAM NEGERI (RPT) (DOMESTIC VESSEL OPERATING PERMIT)'
                                        ]].min(axis=1)

    ### making new dataframe for status with emoji using df_tb_days
    df_cts_status = df_cts_days.copy()
    for i in df_cts_days:
        df_cts_status[i] = df_cts_status[i].apply(lambda x:
                                                '❌' if x < 0 else (
                                                    '⚠️' if x < 30 else(
                                                        '🔲' if pd.isna(x) else '✔️')))
    
    df_tb_simple = df_tb_status[['SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)',
                                'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)',
                                'SERT. PENCEGAHAN PENCEMARAN MINYAK (CERTIFICATE OF INTERNATIONAL OIL POLLUTION PREVENTION (IOPP))',
                                'NEXT ANNUAL',
                                'SERTIFIKAT JAMINAN GANTI RUGI PENCEMARAN MINYAK',
                                'SERTIFIKAT PEMERIKSAAN RAKIT PENYELAMATAN (CERTIFICATE OF LIFERAFT INSPECTION)',
                                'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)',
                                'Others'
                                ]]
    df_tb_simple.rename(columns={
        'SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)':'NATIONALITY & TONNAGE',
        'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)':'SOLAS',
        'SERT. PENCEGAHAN PENCEMARAN MINYAK (CERTIFICATE OF INTERNATIONAL OIL POLLUTION PREVENTION (IOPP))':'POLLUTION',
        'NEXT ANNUAL':'CLASS',
        'SERTIFIKAT JAMINAN GANTI RUGI PENCEMARAN MINYAK':'INSURANCE',
        'SERTIFIKAT PEMERIKSAAN RAKIT PENYELAMATAN (CERTIFICATE OF LIFERAFT INSPECTION)':'LSA & FFA',
        'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)':'HEALTH',
        'Others':'OTHERS',
    }, inplace=True)

    df_ba_simple = df_ba_status[['SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)',
                                'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)',
                                'NEXT ANNUAL',
                                'SERTIFIKAT ASURANSI (CERTIFICATE OF INSURANCE)',
                                'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)',
                                'Others'
                                ]]
    df_ba_simple.rename(columns={
        'SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)':'NATIONALITY & TONNAGE',
        'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)':'SOLAS',
        'NEXT ANNUAL':'CLASS',
        'SERTIFIKAT ASURANSI (CERTIFICATE OF INSURANCE)':'INSURANCE',
        'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)':'HEALTH',
        'Others':'OTHERS',
    }, inplace=True)

    df_cts_simple = df_cts_status[['SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)',
                                'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)',
                                'SERT. PENCEGAHAN PENCEMARAN MINYAK (CERTIFICATE OF INTERNATIONAL OIL POLLUTION PREVENTION (IOPP))',
                                'SERT. GARIS MUAT INTERNASIONAL (CERTIFICATE OF LOAD LINE)',
                                'SERTIFIKAT JAMINAN GANTI RUGI PENCEMARAN MINYAK',
                                'SERTIFIKAT PEMERIKSAAN RAKIT PENYELAMATAN (CERTIFICATE OF LIFERAFT INSPECTION)',
                                'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)',
                                'Others'
                                ]]
    df_cts_simple.rename(columns={
        'SURAT LAUT/ PAS TAHUNAN (CERTIFICATE OF NATIONALITY)':'NATIONALITY & TONNAGE',
        'SERT. KESELAMATAN KONSTRUKSI KAPAL (CERTIFICATE OF SHIP SAFETY CONSTRUCTION)':'SOLAS',
        'SERT. PENCEGAHAN PENCEMARAN MINYAK (CERTIFICATE OF INTERNATIONAL OIL POLLUTION PREVENTION (IOPP))':'POLLUTION',
        'SERT. GARIS MUAT INTERNASIONAL (CERTIFICATE OF LOAD LINE)':'CLASS',
        'SERTIFIKAT JAMINAN GANTI RUGI PENCEMARAN MINYAK':'INSURANCE',
        'SERTIFIKAT PEMERIKSAAN RAKIT PENYELAMATAN (CERTIFICATE OF LIFERAFT INSPECTION)':'LSA & FFA',
        'SERTIFIKAT BEBAS TINDAKAN SANITASI KAPAL (SHIP SANITATION CONTROL EXEMPTON CERTIFICATE)':'HEALTH',
        'Others':'OTHERS',
    }, inplace=True)

    
    data = pd.concat([df_tb_simple, df_ba_simple, df_cts_simple], keys=['Tugboat', 'Barge', 'CTS'])
    data.fillna({'NATIONALITY & TONNAGE':'🔲', 'SOLAS':'🔲', 'POLLUTION':'🔲', 'CLASS':'🔲', 'INSURANCE':'🔲', 'LSA & FFA':'🔲', 'HEALTH':'🔲',
                 }, inplace=True)
    data = data.reset_index()
        
    ## DataFrame to dash table
    data_dashboard = [data.to_dict('records')]
    # tooltip_table_dash = tooltip_table(data)
    
    return data_dashboard
