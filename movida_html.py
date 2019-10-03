# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from scrapy.http import Request
from scrapy import signals, Spider

# informações que queremos obter do anúncio.
field_list = ['preco', 'nome', 'nome_completo', 'modelo', 'quilometragem', 
              'combustivel', 'ano', 'cambio', 'portas', 'cor', 'final_placa']

class CarSpider(Spider):
    name = 'car_spider'
    # domínios permitidos pelo spider.
    allowed_domains = ['movidaseminovos.com.br']
    # site que o spider irá iniciar a coleta.
    start_urls = ['https://busca.movidaseminovos.com.br/filtros/class/usado?sort=11']

    # Função principal do programa, realiza a aquisição.
    def parse(self, response):
        # criando arquivo .csv que terá o resultado dos dados adquiridos.
        pd.DataFrame(columns=field_list).to_csv('output_carros.csv', index=False)
        # itera sobre todas as páginas até a última.
        for i in range(1, int(response.xpath("//li[@class='neemu-pagination-last']/a/@href").extract_first().split('page=')[1])+1):
            yield Request('https://busca.movidaseminovos.com.br/filtros/class/usado?sort=11&page={}'.format(i),
                         callback=self.parse_pagina)

    # Função responsável por adquirir os anúncios de uma página.
    def parse_pagina(self, response):
        # pega as urls dos carros nas páginas.
        carros_url = np.unique(response.css('li#nm-product- > div > a::attr(href)').extract())
        # para cada url, chama a função parse_carro que irá adquirir os dados de um anúncio de carro.
        for carro_url in carros_url:
            yield Request(url='https:'+carro_url, callback=self.parse_carro)

    # Função que realiza a aquisição dos dados de um anúncio.
    def parse_carro(self, response):
        # printando o site em que o crawler está
        print('\n'+str(response)+'\n')
        # Criando um dataframe que irá virar uma linha em nosso .csv de saída.
        item = pd.DataFrame(columns=field_list)
        # coletando o preço e nome do anúncio.
        item.loc[0, 'preco'] = response.css('h2.h3 > b::text').extract_first()
        item.loc[0, 'nome'] = response.css('h1.interno-prod-title::text').extract_first().strip()
        item.loc[0, 'nome_completo'] = response.css('h3.interno-prod-version-title::text').extract_first()
        
        # coletando os atributos disponíveis sobre o carro.
        atributos = ['modelo', 'quilometragem', 'combustivel', 'ano', 'cambio', 'portas', 'cor', 'final_placa']
        valores_atributos = response.css('tbody > tr > td.t-value.h6::text').extract()
        # atribuindo os atributos adquiridos.
        for i, atributo in enumerate(atributos):
            item.loc[0, atributo] = valores_atributos[i]
        
        # salvando as informações coletadas no .csv de saída.
        item.to_csv('output_carros.csv', mode='a', index=False, header=None)