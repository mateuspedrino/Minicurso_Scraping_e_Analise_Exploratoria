# -*- coding: utf-8 -*-
import scrapy
import pandas as pd

# colunas do dataframe.
field_list = ['phrase', 'author', 'tags']

class QuotesToScrapeSpider(scrapy.Spider):
    name = 'quotes_to_scrape'
    # site que o crawler vai iniciar.
    start_urls = ['http://quotes.toscrape.com/']
    # criando um dataframe para salvarmos nossos resultados.
    pd.DataFrame(columns=field_list).to_csv('resultados_quotes.csv', index=False)

    # Função principal do crawler, ela que vai ser responsável por crawlear as coisas.
    def parse(self, response):
        # printando o site em que o crawler está
        print('\n'+str(response)+'\n')
        # coletando os seletores css (div.quote representa as frases, autores e tags.)
        selectors = response.css('div.quote')
        # para cada um dos 'blocos', coleta frase, autor e tags
        for selector in selectors:
            # criando um dataframe na mesma estrutura anterior.
            item = pd.DataFrame(columns=field_list)
            # coletando a frase.
            item['phrase'] = selector.css('span.text::text').extract()
            # coletando o autor.
            item['author'] = selector.css('span > small::text').extract()
            # coletando as tags.
            tags = selector.css('div.tags > a.tag')
            str_tag = ''
            for tag in tags:
                str_tag += tag.css('a.tag::text').extract()[0]+'/'

            # salva a lista de tags até [:-1] para ignorar o último /.
            item['tags'] = str_tag[:-1]
            # salvando os resultados no dataframe criando e appendando no .csv criado no início do programa.
            item.to_csv('resultados_quotes.csv', mode='a', index=False, header=None)

        # coletando endereço da próxima página.
        next_page = response.css('li.next > a::attr(href)').extract_first()
        # caso next_page seja diferente de vazio (valor retornado quando não há mais páginas), avança para a próxima página.
        if(next_page):
            # avança para a próxima página.
            yield response.follow(next_page, callback=self.parse)