require './Apex'


logins = CSV.read('./docs/logins', { :col_sep => "\t" })

A = Apex.new

#logins.each do |fiver, username, password|
#  A.login(username, password)
#  A.find_customers
#  A.find_machines
#  A.machines.each do |dev, hash|
#    records = A.find_transaction_details('10/01/2013', '10/05/2013', hash['siteId'], hash['deviceId'])
#  end
#end

def output(machine, records)
  # expecting position, sku, dispense qty, unit price, pkg qty, currency
  CSV.open('./docs/output', 'a') do |csv|
    records.each do |pos, sku, d_qty, cost, p_qty, curr|
      # attempt to fix erroneous dispense qtys on lockers
      d_qty = 1 if pos.to_i >= 70 and d_qty.to_i > 12
      csv << [machine['companyName'], machine['deviceName'], sku, (d_qty.to_i * p_qty.to_i), cost]
    end
  end
end

A.login()
A.find_customers
A.find_machines
A.machines.each do |dev, hash|
  records = A.find_transaction_details('10/01/2013', '10/05/2013', hash['siteId'], hash['deviceId'])
  # exclude first and last two lines
  output hash, records[1...-2]
end
