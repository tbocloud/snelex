// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Manifest", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Manifest",{
    refresh(frm){
        frm.set_query("truck",function(){
            return{
                filters:{
                    "status":"Available"
                }
            }
                
        })
    },
    truck:function(frm){
        if(frm.truck){
            frappe.db.get_doc("Truck",frm.truck)
        }
    }
})