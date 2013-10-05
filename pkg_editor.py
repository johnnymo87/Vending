from ApexScrape import *
import string


class Editor(Apex):

    def __init__(self, (username, password), customer):
        Apex.__init__(self, (username, password))
        self.target = self.matchCustomer(customer)
        print self.target

    def matchCustomer(self, customer):
        for cust in self.customers:
            if string.lower(customer) in string.lower(cust):
                print 'Customer set to', cust
                return {'comId': self.comId, 'siteId': self.customers[cust]}
        else:
            raise LookupError(self.target, 'not found!')

    def findParts(self, searchText):
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
            ('searchText', searchText)
            ))
        request = self.s.post(url, params)
        data = request.content.split('|')
        data = [json.loads(d) for d in data]
        if len(data[6]) < 1:
            raise LookupError('No parts found for', SKU)
        return data[6]

    def updatePart(self, part, updates):
        for up in updates:
            assert up in part
            part[up] = updates[up]

    def postChanges(self, part):
        print 'Updating {} : {}'.format(part['productNum1'], part['name'])
        url = 'https://fastsolutions.mroadmin.com/ProductManager/product_editSiteProduct.action'                
        params = OrderedDict((
                    ('siteProductId', 'editSiteProduct.site_product_id'),
                    ('name', 'editSiteProduct.name'),
                    ('productNum1', 'editSiteProduct.product_num1'),
                    ('productNum2', 'editSiteProduct.product_num2'),
                    ('productNum3', 'editSiteProduct.product_num3'),
                    ('productNam1', 'editSiteProduct.product_name1'),
                    ('ManufacturerName', 'editSiteProduct.manufacturer_name'),
                    ('productSize', 'editSiteProduct.product_size'),
                    ('productColor', 'editSiteProduct.product_color'),
                    ('unitPrice', 'editSiteProduct.unit_price'),
                    ('packagePrice', 'editSiteProduct.package_price'),
                    ('packageQty', 'editSiteProduct.package_qty'),
                    ('unitCost', 'editSiteProduct.unit_cost'),
                    ('description', 'editSiteProduct.description'),
                    ('supplierId', 'editSiteProduct.supplier_id'),
                    ('siteId', 'editSiteProduct.site_id'),
                    ('isCritical', 'editSiteProduct.is_critical'),
                    ('productGroupId', 'editSiteProduct.product_group_id'),
                    ('flagEdit', 'flagEdit')
                ))
        real_params = OrderedDict()
        for param in params:
            if param in part:
                real_params[params[param]] = str(part[param])
            else:
                real_params[params[param]] = ''
        request = self.s.post(url, real_params)

           


def readTemplate(filename):
    """line[0] = SKU, line[1] = Description"""
    attributes = ['ManufacturerName', 'description', 'flagEdit', 'isCritical', 'name', \
                  'packagePrice', 'packageQty', 'productColor', 'productGroupId', \
                  'productNam1', 'productNum1', 'productNum2', 'productNum3', \
                  'productSize', 'siteId', 'siteProductId', 'supplierId', 'unitCost', \
                  'unitPrice']
    updates = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip().split('\t')
            if len(line) % 2 != 1:
                raise ValueError('Even number of columns, cannot make key-value pairs')
            pairs = line[1:]
            for p in pairs[0::2]:
                assert p in attributes
            updates[line[0]] = dict(zip(pairs[0::2], pairs[1::2]))
    return updates
        

if __name__ == '__main__':
    updates = readTemplate('Hudson Rename.txt')
    editor = Editor(('STOREFLORM', 'password'), 'Hudson Tool Tool Room')
    for up in updates:
        parts = editor.findParts(up)
        part = [ p for p in parts if p['productNum1'] == up ]
        assert len(part) == 1
        part = part[0]
        editor.updatePart(part, updates[up])
        editor.postChanges(part)
