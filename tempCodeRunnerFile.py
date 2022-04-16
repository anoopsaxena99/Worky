row in values:
    #     # row[0] is an number
    #     cur = mysql.get_db().cursor()

    #     cur.execute(
    #         "SELECT a1.offer_id FROM ActiveOffers AS a1 INNER JOIN Offers ON a1.offer_id=Offers.offer_id WHERE Offers.CMobileNo != '{}' AND a1.offer_id NOT IN (SELECT offer_id FROM Request_Table WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM RejectedRequest WHERE WMobileNo='{}') AND a1.offer_id NOT IN (SELECT offer_id FROM AcceptedRequest WHERE WMobileNo='{}') AND a1.offer_id IN  (With b1 as (SELECT b3.offer_id,DailyWage,Labour,Mechanic,Electrician,Carpentry FROM ActiveOffers AS b3 INNER JOIN Offers ON b3.offer_id=Offers.offer_id),b2 as (SELECT * FROM Worker where WMobileNo='{}') select b1.offer_id from b1,b2 where b1.DailyWage>=b2.MinPrice AND ((b1.Labour=1 and b2.Labour=1) or (b1.Electrician=1 and b2.Electrician=1) or (b1.Carpentry=1 and b2.Carpentry=1) or (b1.Mechanic=1 and b2.Mechanic=1)) )".format(row[1], row[1], row[1], row[1], row[1]))
    #     data = cur.fetchall()