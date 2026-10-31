"""Análise dos dados da Hermex Log (NPS e SLA). Uso: python scripts/analise.py"""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REG = {'SP':'Sudeste','RJ':'Sudeste','MG':'Sudeste','ES':'Sudeste','BA':'Nordeste','PE':'Nordeste','CE':'Nordeste','MA':'Nordeste',
       'RS':'Sul','PR':'Sul','SC':'Sul','GO':'Centro-Oeste','AM':'Norte','PA':'Norte'}
SLA = {'Sudeste':(2,5),'Sul':(3,6),'Centro-Oeste':(4,7),'Nordeste':(6,12),'Norte':(8,16)}

d = pd.read_csv('data/pesquisa_satisfacao.csv', parse_dates=['data_pedido','data_envio','data_recebimento'])
d['regiao'] = d.estado.map(REG)
d['dias_ate_envio'] = (d.data_envio - d.data_pedido).dt.days
d['dias_ate_entrega'] = (d.data_recebimento - d.data_pedido).dt.days
d['dias_transporte'] = (d.data_recebimento - d.data_envio).dt.days
d['promotor'] = (d.nota_nps > 8).astype(int)
d['detrator'] = (d.nota_nps < 7).astype(int)
d['dentro_sla_pedido'] = d.apply(lambda r: r.dias_ate_entrega <= SLA[r.regiao][1], axis=1)
d['dentro_sla_transporte'] = d.apply(lambda r: r.dias_transporte <= SLA[r.regiao][1], axis=1)

def agg(g):
    return pd.Series({'Respostas':len(g),'Promotores':g.promotor.sum(),'Detratores':g.detrator.sum(),
        'NPS (%)':round((g.promotor.sum()-g.detrator.sum())/len(g)*100,1),'Nota média':round(g.nota_nps.mean(),2),
        'Dias até envio':round(g.dias_ate_envio.mean(),1),'Dias até entrega':round(g.dias_ate_entrega.mean(),1),
        'Dias transporte':round(g.dias_transporte.mean(),1),'% dentro SLA (pedido→entrega)':round(g.dentro_sla_pedido.mean()*100,1)})
uf = d.groupby('estado').apply(agg).sort_values('NPS (%)')
rg = d.groupby('regiao').apply(agg).sort_values('NPS (%)')
geral = agg(d)
d['faixa'] = pd.cut(d.dias_ate_entrega,[0,5,8,11,30],labels=['até 5 dias','6–8 dias','9–11 dias','12+ dias'])
fx = d.groupby('faixa',observed=True).apply(lambda g: pd.Series({'Pedidos':len(g),'NPS (%)':round((g.promotor.sum()-g.detrator.sum())/len(g)*100,1),'Nota média':round(g.nota_nps.mean(),2)}))
corr = d[['nota_nps','dias_ate_entrega']].corr().iloc[0,1]

# Classificação manual de referência dos 31 detratores (para comparar com o Gemini)
REF = {'P002':'Embalagem','P004':'Atraso','P006':'Defeito','P007':'Atendimento','P009':'Atraso','P012':'Atraso','P013':'Outro',
 'P014':'Atendimento','P016':'Atraso','P018':'Defeito','P020':'Atraso','P021':'Defeito','P024':'Atraso','P026':'Atendimento',
 'P027':'Atraso','P030':'Atraso','P031':'Atraso','P032':'Defeito','P035':'Atraso','P036':'Atraso','P039':'Outro','P041':'Atraso',
 'P044':'Atraso','P046':'Outro','P047':'Embalagem','P049':'Atraso','P050':'Defeito','P052':'Atraso','P055':'Atraso','P057':'Atraso','P059':'Atraso'}
det = d[d.detrator==1][['id_pedido','estado','regiao','nota_nps','comentario']].copy()
det['categoria_referencia'] = det.id_pedido.map(REF)
assert det.categoria_referencia.notna().all()
det.to_csv('data/detratores_classificacao_referencia.csv', index=False)
cats = det.categoria_referencia.value_counts()

h = pd.read_csv('data/handoff_vendas_posvenda.csv')
x = d.merge(h[['id_pedido','valor_pedido','responsavel_posvenda']], on='id_pedido')
risco = x[x.detrator==1].valor_pedido.sum(); total = x.valor_pedido.sum()

# Gráficos
c = ['#c0392b' if v<0 else '#2c6fbb' for v in uf['NPS (%)']]
ax = uf['NPS (%)'].plot.barh(color=c, figsize=(7,5)); ax.set_title('NPS por estado (%)'); ax.axvline(0,color='k',lw=.8); plt.tight_layout(); plt.savefig('screenshots/grafico_nps_por_estado.png',dpi=130); plt.close()
ax = uf['Dias até entrega'].sort_values().plot.barh(color='#2c6fbb', figsize=(7,5)); ax.set_title('Média de dias do pedido até a entrega, por estado'); plt.tight_layout(); plt.savefig('screenshots/grafico_dias_entrega_por_estado.png',dpi=130); plt.close()
fig,ax=plt.subplots(figsize=(6,4)); ax.scatter(d.dias_ate_entrega,d.nota_nps,alpha=.6,color='#2c6fbb'); ax.set_xlabel('Dias do pedido até a entrega'); ax.set_ylabel('Nota NPS'); ax.set_title(f'Nota x prazo (correlação = {corr:.2f})'); plt.tight_layout(); plt.savefig('screenshots/grafico_nota_vs_prazo.png',dpi=130); plt.close()

def md(df): return df.reset_index().to_markdown(index=False)
out = f"""# Análise dos dados — NPS e SLA da Hermex Log

> Gerado por `scripts/analise.py` a partir de `data/pesquisa_satisfacao.csv` (60 respostas, P001–P060, abril/2025).
> Definições: Promotor = nota ≥ 9; Detrator = nota ≤ 6; NPS = %promotores − %detratores.
> Use estes números para **validar** os campos calculados do Looker Studio.

## Indicadores gerais
- Respostas: **{int(geral['Respostas'])}** | Promotores: **{int(geral['Promotores'])}** | Detratores: **{int(geral['Detratores'])}** | Neutros: **{60-int(geral['Promotores'])-int(geral['Detratores'])}**
- **NPS geral: {geral['NPS (%)']}%** (nota média {geral['Nota média']})
- Média de dias até o envio: **{geral['Dias até envio']}** | até a entrega: **{geral['Dias até entrega']}** | só transporte: **{geral['Dias transporte']}**
- Correlação entre nota e dias até a entrega: **{corr:.2f}** (quanto maior o prazo, menor a nota)
- Se o detrator fosse `nota < 6` (como no enunciado da etapa 3), seriam {int((d.nota_nps<6).sum())} detratores e NPS de {round((d.promotor.sum()-(d.nota_nps<6).sum())/60*100,1)}%. As 4 notas 6 (P014, P026, P031, P047) ficariam sem tratamento.

## Por região
{md(rg)}

## Por estado
{md(uf)}

## NPS por faixa de prazo (pedido → entrega)
{md(fx)}

## Classificação dos {len(det)} detratores (referência manual)
{cats.to_markdown()}

Vários comentários citam mais de um problema (ex.: P002 "caixa amassada e fora do prazo"); a categoria de referência é a predominante. Compare com a saída do Gemini no n8n.

## Handoff × detratores
Dos 30 pedidos com dados de handoff, os detratores representam **R$ {risco:,.2f}** de **R$ {total:,.2f}** ({risco/total*100:.0f}% do valor).

## Gráficos
![NPS por estado](../screenshots/grafico_nps_por_estado.png)
![Dias até entrega](../screenshots/grafico_dias_entrega_por_estado.png)
![Nota x prazo](../screenshots/grafico_nota_vs_prazo.png)
"""
open('docs/06_analise_dados.md','w').write(out)
print(out[:3500]); print(d.dentro_sla_pedido.mean(), d.dentro_sla_transporte.mean())
