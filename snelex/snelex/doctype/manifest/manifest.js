// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt


frappe.ui.form.on("Manifest",{
    refresh:function(frm){
        frm.set_query("truck",function(){
            return{
                filters:{
                    "status":"Available"
                }
            }

        })
    },
    get_consignment_details:function(frm){
      if(!frm.doc.manifest_date || !frm.doc.location){
        frappe.throw("Select the Manifest Date and Location")
      }
      frappe.call({
          method:'snelex.snelex.doctype.manifest.manifest.get_consignment_details',
          args:{
           manifest_date:frm.doc.manifest_date,
           location:frm.doc.location
          },
          callback:function(r){
              if (r.message){
                  frm.clear_table("consignment_details")
                  r.message.forEach(function(row)
              {
                  let child=frm.add_child("consignment_details");
                  child.consignment_number=row.name;
                  child.consignment_date=row.consignment_date;
                  child.consignee=row.consignee_customer;
                  child.shipper=row.shipper;
                  child.remarks=row.remarks;
              });
              frm.refresh_field("consignment_details")

              }
          }
      });
    }
});
