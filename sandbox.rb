require './Apex'

#class Download < Apex
#  def initialize(username, password)
#    login(username, password)
#    find_customers
#    find_machines
#  end
#
#  def download_transactions
#
#  end
#end

A = Apex.new
A.login()