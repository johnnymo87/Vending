require 'sinatra'
require 'mechanize'
require 'json'

require 'csv'

class CSVParser < Mechanize::File
  attr_reader :csv

  def initialize uri = nil, response = nil, body = nil, code = nil
    super uri, response, body, code
    @csv = CSV.parse body
  end
end

class Apex
  def initialize
    @browser = Mechanize.new
    @search_fields = 'Motor Position|MotorPosition,Product SKU|ProductNum1,Quantity Dispensed|QtyDispensed,Unit Price|SymbolCodeUnitPrice,Package Qty|PackageQty'
  end

  attr_accessor :search_fields
  attr_reader :browser, :store, :customers, :machines


  def login(username, password)
    url = 'https://fastsolutions.mroadmin.com/APEX-Login/account_login.action'
    login_data = {'user.login_id' => username, 'user.password' => password}
    response = @browser.post(url, login_data).content
    if response =~ /Invalid login!/
      {}
    else
      # comId not available unless I navigate further
      url = 'https://fastsolutions.mroadmin.com/Apex-Device/siteAction_getSelectedCompanyList.action'
      response = @browser.get(url).content
      response = JSON.parse(response)[0]
      @store = response['tableId']
      # throw out useless data
      response = {'name' => response['name'], 'comId' => response['tableId']}
      response
    end
  end

  def find_customers
    # @customers[0].keys =>
    # ["state", "siteName", "siteId", "statusCd", "class", "deviceCount", "city", "address1"]
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/siteAction_viewSitesOwnedByMyCompany.action'
    response = @browser.get(url).content.split('|')
    @customers = JSON.parse response[-2]
    #@customers = Hash[@customers.map { |c| [c['siteId'], c] }]
    @customers
  end

  def find_machines
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/deviceBinAction_initDevicesList.action'
    @machines = {}
    @customers.each do |customer|
      params = {
          'actionSequence' => 20, 'requestId' => customer['siteId'],'comId' => @store,
          'newSortColumn' => 0, 'oldSortColumn' => 0, 'sortFlag' => 'null',
          'sortCancel' => 0, 'siteType' => 'owner'}
      response = @browser.get(url, params).content.split('|')
      machines = JSON.parse(response[-2])
      customer['machines'] = []
      machines.each do |machine|
        customer['machines'] << machine['deviceId']
        machine['siteId'] = customer['siteId']
        @machines[machine['deviceId']] = machine
      end
    end
    @machines
  end

  def find_parts_info(site_id)
    parts_info = {}
    url = 'https://fastsolutions.mroadmin.com/ProductManager/product_listSiteProductAjax.action'
    params = {'page' => 1, 'companyId' => @store, 'siteId' => site_id}
    response = @browser.get(url, params).content.split('|')
    pages = Nokogiri::HTML(response[0])
    pages = pages.at_css('.table_head').content
    pages = pages.scan(/\w+/)[4].to_i
    (0...pages).each do
      rows = JSON.parse(response[-2])
      rows.each do |row|
        sku = row['productNum1'][/[\d\w\[\]-]+/]
        parts_info[sku] = row
      end
      params['page'] += 1
      response = @browser.get(url, params).content.split('|')
    end
    parts_info
  end

  ### Incomplete, works for lockers only

  def find_bin_ids(site_id, device_id, empty=true)
    empty ? command = 'Add' : command = 'Remove'
    bin_ids = {}
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_detailPOG.action'
    params = {'comId' => @store, 'siteId' => site_id, 'requestId' => device_id}
    response = @browser.get(url, params).content
    response = Nokogiri::HTML(response)
    row_ids = response.css('.tableContainer tr')
    row_ids = row_ids.select { |node| node.values[0].to_s =~ /tr/ or node.values[0].to_s =~ /lockerTr/ }
    # ['lockerTr52', 'lockerTr53']
    row_ids = row_ids.collect { |node| node.values[0].to_s.scan(/[\d]+/)[0] }
    row_ids.each do |id|
      addLockerItem = response.css("#locker#{command}Text#{id} a")
      if !addLockerItem.empty?
        addLockerItem = addLockerItem[0]['href'].to_s
        loc_code = addLockerItem.scan(/LOC[\d]+/)[0]
        position = addLockerItem.scan(/[\d]*?\.[\d]/)[0]
        bin_ids[position] = loc_code
      end
    end
    bin_ids
  end

  def assign_product(position, loc_id, spd_id)
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_updateLocker.action'
    params = {'locker.locker_id' => loc_id, 'motorPosition' => position, 'siteProduct.siteProductId' => spd_id}
    @browser.get(url, params)
  end

  def edit_values(loc_id, count, max, min, critical, sku)
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_saveLockers.action'
    params = {'lockersArray' => "#{loc_id},#{count},#{max},#{min},#{critical},#{sku}"}
    @browser.post(url, params)
  end

  ###

  def find_machine_counts(site_id, device_id)
    counts = {}
    url = 'https://fastsolutions.mroadmin.com/Apex-Device/devicePOGAction_detailPOG.action'
    params = {'comId' => @store, 'siteId' => site_id, 'requestId' => device_id}
    response = @browser.get(url, params).content
    response = Nokogiri::HTML(response)
    row_ids = response.css('.tableContainer tr')
    row_ids = row_ids.select { |node| node.values[0].to_s =~ /tr/ or node.values[0].to_s =~ /lockerTr/ }
    # ['lockerTr52', 'lockerTr53']
    row_ids.collect { |node| node.values[0].to_s}
    row_ids.each do |id|
      row = response.css("tr##{id} td")
      row = row.collect { |node| node.content.to_s.strip}[0...-2]
      if id =~ /tr/
        row = {'position' => row[0], 'description' => row[1], 'sku' => row[2], 'count' => row[3],
               'capacity' => row[4], 'max' => row[5], 'min' => row[6], 'critical' => row[7],
               'available_offline' => row[8], 'status' => row[9]}
      elsif id =~ /lockerTr/
        # lockers have no capacity
        row = {'position' => row[0], 'description' => row[1], 'sku' => row[2], 'count' => row[3],
               'max' => row[4], 'min' => row[5], 'critical' => row[6], 'available_offline' => row[7],
               'status' => row[8]}
      end
      counts[row['position'].to_i] = row
    end
    counts
  end

  def find_transaction_details(begin_date, end_date, site_id='', device_id='')
    url = 'https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_viewTransaction.action'
    params = {'page' => 1, 'beginDate' => begin_date, 'endDate' => end_date, 'checkBoxFileds' => @search_fields,
              'companyId' => @store, 'sideIdTmp' => site_id, 'deviceId' => device_id, 'searchFlag' => 'SEARCH', 'companyType' => 'OWNER'}
    @browser.get(url, params)
    url = 'https://fastsolutions.mroadmin.com/ReportManager/transactionReportAction_downLoadCsv.action'
    params = {'hierarchyCd' => 'undefined', 'nodeId' => 'undefined', 'beginDate' => begin_date, 'endDate' => end_date,
              'companyId' => @store, 'siteIdTmp' => site_id, 'deviceId' => device_id, 'searchFlag' => 'SEARCH',
              'checkBoxFileds' => @search_fields,
              'companyType' => 'OWNER', 'searchBy' => 'sku'}
    @browser.pluggable_parser.csv = CSVParser
    @browser.get(url, params).content
  end


  def find_transaction_summary(site_id, device_id, begin_date, end_date)
    url = 'https://fastsolutions.mroadmin.com/ReportManager/usageReportAction_getOwnerReportByDeviceBinValue.action'
    params = {'company.companyId' => @store, 'siteIdTmp' => site_id, 'deviceIdTemp' => device_id,
              'beginDate' => begin_date, 'endDate' => end_date, 'reportType' => 'owner', 'currencyCode' => 'USD'}
    response = @browser.get(url, params).content.split('|')
    response = JSON.parse(response[-1])[0...-1]
    response
  end
end