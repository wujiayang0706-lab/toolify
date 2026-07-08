#!/usr/bin/env python3
"""Pre-render dropdown options and rates table in the currency converter HTML."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(BASE, 'currency-converter', 'index.html')

with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

currencies = [
    ('USD','US Dollar','$'),('EUR','Euro','\u20ac'),('JPY','Japanese Yen','\u00a5'),
    ('GBP','British Pound','\u00a3'),('CNY','Chinese Yuan','\u00a5'),('KRW','Korean Won','\u20a9'),
    ('AUD','Australian Dollar','A$'),('CAD','Canadian Dollar','C$'),('CHF','Swiss Franc','Fr'),
    ('HKD','Hong Kong Dollar','HK$'),('SGD','Singapore Dollar','S$'),('INR','Indian Rupee','\u20b9'),
    ('BRL','Brazilian Real','R$'),('RUB','Russian Ruble','\u20bd'),('MXN','Mexican Peso','$'),
    ('ZAR','South African Rand','R'),('TRY','Turkish Lira','\u20ba'),('THB','Thai Baht','\u0e3f'),
    ('TWD','New Taiwan Dollar','NT$'),('SEK','Swedish Krona','kr'),('NOK','Norwegian Krone','kr'),
    ('DKK','Danish Krone','kr'),('PLN','Polish Zloty','z\u0142'),('CZK','Czech Koruna','K\u010d'),
    ('HUF','Hungarian Forint','Ft'),('NZD','New Zealand Dollar','NZ$'),('AED','UAE Dirham','\u062f.\u0625'),
    ('SAR','Saudi Riyal','\u0631.\u0633'),('MYR','Malaysian Ringgit','RM'),('IDR','Indonesian Rupiah','Rp'),
    ('PHP','Philippine Peso','\u20b1'),('VND','Vietnamese Dong','\u20ab'),
]

fallback = {
    'USD':1,'EUR':0.92,'JPY':150,'GBP':0.79,'CNY':7.25,'KRW':1380,'AUD':1.52,'CAD':1.36,
    'CHF':0.90,'HKD':7.83,'SGD':1.35,'INR':83.5,'BRL':5.15,'RUB':92,'MXN':17.5,
    'ZAR':18.5,'TRY':32.5,'THB':36.5,'TWD':32,'SEK':10.5,'NOK':10.8,'DKK':6.85,
    'PLN':4.0,'CZK':23,'HUF':360,'NZD':1.65,'AED':3.67,'SAR':3.75,'MYR':4.7,
    'IDR':16300,'PHP':57,'VND':25400,
}

def gen_options(selected=None):
    opts = []
    for code, name, symbol in currencies:
        sel = ' selected' if code == selected else ''
        opts.append('<option value="{}"{}>{} \u2014 {}</option>'.format(code, sel, code, name))
    return '\n          '.join(opts)

popular = ['EUR','JPY','GBP','CNY','KRW','AUD','CAD','CHF','HKD','SGD','INR','BRL','RUB','MXN','ZAR']

def gen_rows():
    rows = []
    for code in popular:
        name = next(n for c,n,s in currencies if c==code)
        symbol = next(s for c,n,s in currencies if c==code)
        rate = fallback[code]
        if code in ('JPY','KRW','IDR','VND','CLP','PYG'):
            rate_str = str(round(rate))
            inv_str = '{:.6f}'.format(1/rate)
        else:
            rate_str = '{:.2f}'.format(rate)
            inv_str = '{:.4f}'.format(1/rate)
        rows.append('<tr><td><span class="rate-currency">{}</span> <span style="color:var(--text-muted);font-size:13px">{}</span></td><td class="rate-value">{} {}</td><td class="rate-inverse">{} {}</td></tr>'.format(code, name, symbol, rate_str, inv_str, code))
    return '\n          '.join(rows)

# Replace empty selects with pre-populated ones
from_opts = gen_options('USD')
to_opts = gen_options('EUR')

html = html.replace(
    '<select id="fromCurrency"></select>',
    '<select id="fromCurrency">\n          ' + from_opts + '\n        </select>'
)
html = html.replace(
    '<select id="toCurrency"></select>',
    '<select id="toCurrency">\n          ' + to_opts + '\n        </select>'
)

# Replace empty tbody
rows_html = gen_rows()
html = html.replace(
    '<tbody id="ratesTableBody"></tbody>',
    '<tbody id="ratesTableBody">\n          ' + rows_html + '\n        </tbody>'
)

# Replace initial result
html = html.replace(
    '<div class="result-amount" id="resultAmount">\u2014</div>',
    '<div class="result-amount" id="resultAmount">\u20ac 92.00</div>'
)
html = html.replace(
    '<div class="result-rate" id="resultRate">\u2014</div>',
    '<div class="result-rate" id="resultRate">1 USD = 0.92 EUR  \u00b7  1 EUR = 1.0870 USD</div>'
)

# Replace loading status text
html = html.replace(
    'Loading exchange rates...',
    'Showing cached rates'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done! Pre-rendered {} options and {} table rows'.format(len(currencies), len(popular)))
