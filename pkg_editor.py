from ApexScrape import *

FLGAN = Apex(('FLGANStore', 'password'))

params = OrderedDict((
            ('actionSequence', '3'),
            ('RequestId', 'undefined'),
            ('newSortColumn', '0'),
            ('oldSortColumn', '0'),
            ('sortFlag', 'null'),
            ('sortCancel', '0'),
            ('companyId', 'COM000002212'),
            ('siteId', 'SIT100110786'),
            ('searchText', '0200803')
        ))
request = FLGAN.s.post("https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action", params=params)      

##url = 'https://fastsolutions.mroadmin.com/ProductManager/product_editSiteProduct.action'
##params = OrderedDict((
##            ('editSiteProduct.site_product_id', 'SPD100688935'),
##            ('editSiteProduct.name', 'Yellow Stick Marker 3pk'),
##            ('editSiteProduct.product_num1', '0200803'),
##            ('editSiteProduct.product_num2', ''),
##            ('editSiteProduct.product_num3', ''),
##            ('editSiteProduct.product_name1', ''),
##            ('editSiteProduct.manufacturer_name', ''),
##            ('editSiteProduct.product_size', ''),
##            ('editSiteProduct.product_color', ''),
##            ('editSiteProduct.unit_price', 5.13),
##            ('editSiteProduct.package_price', 15.39),
##            ('editSiteProduct.package_qty', 1),
##            ('editSiteProduct.unit_cost', 0.01),
##            ('editSiteProduct.description', 'Yellow Stick Marker 3pk'),
##            ('editSiteProduct.supplier_id', 'COM000002212'),
##            ('editSiteProduct.site_id', 'SIT100110786'),
##            ('editSiteProduct.is_critical', 'Y'),
##            ('editSiteProduct.product_group_id', ''),
##            ('flagEdit', '')
##	))
##
##request = FLGAN.s.post(url, params)
print request.content
