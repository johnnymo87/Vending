from ApexScrape import *
import string


class Editor(Apex):

    def __init__(self, (username, password), customer, filename):
        Apex.__init__(self, (username, password))
        self.target = self.matchCustomer(customer)
        print self.target
        self.records = self.readTemplate(filename)

    def matchCustomer(self, customer):
        for cust in self.customers:
            if string.lower(customer) in string.lower(cust):
                print 'Customer set to', cust
                return {'comId': self.customers[cust], 'siteId': self.comId}
        else:
            raise LookupError(self.target, 'not found!')

    def readTemplate(self, filename):
        """line[0] = SKU, line[1] = Description"""
        records = {}
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip().split('\t')
                records[line[0]] = line[1]
##        print records
        return records

    def updateName(self, SKU):
        print 'Updating name for', SKU, ':', self.records[SKU]
        url = "https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action"
        params = OrderedDict((
            ('actionSequence', 3),
            ('RequestId', 'undefined'),
            ('newSortColumn', 0),
            ('oldSortColumn', 0),
            ('sortFlag', 'null'),
            ('sortCancel', 0),
            ('companyId', self.target['comId']),
            ('siteId', self.target['siteId']),
            ('searchText', SKU)
            ))
        request = self.s.post(url, params)
        data = request.content.split('|')
        data = [json.loads(d) for d in data]
        return data[7:][0]

if __name__ == '__main__':
    editor = Editor(('STOREFLORM', 'password'), 'Hudson Tool Tool Room', 'Hudson Rename.txt')
    first = editor.records.keys()[0]
    data = editor.updateName(first)
    

##FLGAN = Apex(('FLGANStore', 'password'))
##
##params = OrderedDict((
##            ('actionSequence', '3'),
##            ('RequestId', 'undefined'),
##            ('newSortColumn', '0'),
##            ('oldSortColumn', '0'),
##            ('sortFlag', 'null'),
##            ('sortCancel', '0'),
##            ('companyId', 'COM000002212'),
##            ('siteId', 'SIT100110786'),
##            ('searchText', '0200803')
##        ))
##request = FLGAN.s.post("https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action", params=params)      

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
##print request.content
