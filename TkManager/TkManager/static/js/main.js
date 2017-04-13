$(document).ready(function() {


    baseSettings = {
        "processing": true,
        "serverSide": true,
        "destroy": true,
        "pagingType" : "full_numbers",
        "autoWidth" : false,
        "scrollCollapse": true,
        "ordering": true,
        "pageLength": 15,
        "lengthMenu" : [[15, 50, 100], ["15", "50", "100"]],
        "language" : {
          "processing" : "数据读取中...",
          "lengthMenu" : "显示_MENU_条 ",
          "zeroRecords" : "没有您要搜索的内容",
          "info" : "从_START_ 到 _END_ 条记录 - 查询到的记录数为 _TOTAL_ 条",
          "infoEmpty" : "记录数为0",
          "infoFiltered" : "(全部记录数 _MAX_  条)",
          "infoPostFix" : "",
          "search" : "搜索",
          "url" : "",
          "paginate" : {
              "first" : "第一页",
              "previous" : " 上一页",
              "next" : " 下一页 ",
              "last" : "最后一页"
          }
        }
    };

    datatable_param = {
        "all_order" : {
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "source", "orderable": true },
              { "name" : "type", "orderable": false },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"], [1], [2], [4], [5]],
          "ajax" : {
              "url":  "/order/all_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },

        "apply_order" : {
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "source", "orderable": true },
              { "name" : "type", "orderable": false },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"], [1], [2], [4], [5]],
          "ajax" : {
              "url":  "/order/apply_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },

        "promotion_order" : {
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "source", "orderable": true },
              { "name" : "type", "orderable": false },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"], [1], [2], [4], [5]],
          "ajax" : {
              "url":  "/order/promotion_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },

        "loan_order" : {
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "source", "orderable": true },
              { "name" : "type", "orderable": false },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"], [1], [2], [4], [5]],
          "ajax" : {
              "url":  "/order/loan_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },
        "pay_loan_mifan" : {
           "aoColumnDefs": [
            {
                // The `data` parameter refers to the data for the cell (defined by the
                // `data` option, which defaults to the column being worked with, in
                // this case `data: 0`.
                "render": function ( data, type, row ) {
                    return '<input type="checkbox" '+ 'value =' + data  +  ' />' + data;
                },
                "targets": 0
            },
            { "visible": false,  "targets": [1,4,5,14] }
                    ],
          "columns": [
              { "data" : "id", "orderable": true },
              { "data" : "uid", "orderable": true },
              { "data" : "order_number", "orderable": false},
              { "data" : "name", "orderable" : false },
              { "data" : "card_id", "orderable" : false },
              { "data" : "channel", "orderable" : false },
              { "data" : "amount", "orderable": true },
              { "data" : "repay_amount", "orderable": true },
              { "data" : "strategy", "orderable": false },
              { "data" : "apply_time", "orderable": true },
              { "data" : "getpay_time", "orderable": false },
              { "data" : "status", "orderable": false },
              { "data" : "mifan_status", "orderable": false },
              { "data" : "bank_type", "orderable": false },
              { "data" : "DT_RowId" , "orderable": false }
          ],
          "order" : [],
          "ajax" : {
              "url":  "/operation/pay_loan_json",
              "data": function (d) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.mifan = "mifan";
                  d.query_str = $("#query_str").val();
                  d.query_type = $("#query_type").val();
                  d.query_strategy_type = $("#query_strategy_type").val();
              }
          }
        },


        "pay_loan_mifan_account" : {
           "aoColumnDefs": [
            {
                // The `data` parameter refers to the data for the cell (defined by the
                // `data` option, which defaults to the column being worked with, in
                // this case `data: 0`.
                "render": function ( data, type, row ) {
                    return '<input type="checkbox" '+ 'value =' + data  +  ' />' + data;
                },
                "targets": 0
            },
            { "visible": false,  "targets": [3,4,14 ] }
                    ],
          "columns": [
              { "data" : "id", "orderable": true },
              { "data" : "uid", "orderable": true },
              { "data" : "order_number", "orderable": false},
              { "data" : "name", "orderable" : false },
              { "data" : "card_id", "orderable" : false },
              { "data" : "channel", "orderable" : false },
              { "data" : "amount", "orderable": true },
              { "data" : "repay_amount", "orderable": true },
              { "data" : "strategy", "orderable": false },
              { "data" : "apply_time", "orderable": true },
              { "data" : "getpay_time", "orderable": false },
              { "data" : "status", "orderable": false },
              { "data" : "mifan_status", "orderable": false },
              { "data" : "bank_type", "orderable": false },
              { "data" : "DT_RowId" , "orderable": false }
          ],

          "order" : [],
          "ajax" : {
              "url":  "/operation/pay_loan_json",
              "data": function (d) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.mifan = "mifan_status";
                  d.query_str = $("#query_str").val();
                  d.query_type = $("#query_type").val();
                  d.query_strategy_type = $("#query_strategy_type").val();
              }
          }
        },

        "check_repay" : {
            "aoColumnDefs": [
                { "visible": false,  "targets": [0] }
            ],
            "columns": [
                { "name" : "id", "orderable" : true },
                { "name" : "uid", "orderable": false },
                { "name" : "username", "orderable": false },
                { "name" : "repay_type", "orderable": true },
                { "name" : "create_at", "orderable": true },
                { "name" : "staff", "orderable": false },
                { "name" : "status", "orderable": true },
                { "name" : "operation", "orderable": false },
            ],
            "order" : [[0, "desc"]],
            "language" :{
                "sSearchPlaceholder": "ID/姓名/手机/身份证/订单号",
            },
            "ajax" : {
                "url":  "/audit/check_repay_json",
                "data": function ( d ) {
                    d.status = $("#statusBox").attr("name");
                    d.type = $("#typeBox").attr("name");
                    d.time = $("#timeBox").attr("name");
                    d.stime = $("#timeBox").attr("stime");
                    d.etime = $("#timeBox").attr("etime");
                }
            },
            "drawCallback": function () {
                $(".do_check").click(function(e) {
                    do_check($(this).attr("name"), "#check_modal");
                });
            }
        },

        "pay_loan" : {
         "aoColumnDefs": [
          { "visible": false,  "targets": [0,4,14] }
          ],
          "columns": [
              { "data" : "id", "orderable": true },
              { "data" : "uid", "orderable": true },
              { "data" : "order_number", "orderable": false},
              { "data" : "name", "orderable" : false },
              { "data" : "card_id", "orderable" : false },
              { "data" : "channel", "orderable" : false },
              { "data" : "amount", "orderable": true },
              { "data" : "repay_amount", "orderable": true },
              { "data" : "strategy", "orderable": false },
              { "data" : "apply_time", "orderable": true },
              { "data" : "getpay_time", "orderable": false },
              { "data" : "status", "orderable": false },
              { "data" : "mifan_status", "orderable": false },
              { "data" : "bank_type", "orderable": false },
              { "data" : "DT_RowId" , "orderable": false }
          ],
          "order" : [],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证/订单号",
          },
          "ajax" : {
              "url":  "/operation/pay_loan_json",
              "data": function (d) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.query_str = $("#query_str").val();
                  d.query_type = $("#query_type").val();
                  d.query_strategy_type = $("#query_strategy_type").val();
              }
          }
        },

        "repay_loan" : {
          "aoColumnDefs": [
                { "visible": false,  "targets": [0] }
          ],
          "columns": [
              { "data" : "id", "orderable": true },
              { "data" : "uid", "orderable": true },
              { "data" : "order_number", "orderable": false},
              { "data" : "name", "orderable" : false },
              { "data" : "card_id", "orderable": false },
              { "data" : "amount", "orderable": true },
              { "data" : "repay_amount", "orderable": true },
              { "data" : "strategy", "orderable": false },
              { "data" : "bank_data", "orderable": true },
              { "data" : "apply_time", "orderable": true },
              { "data" : "getpay_time", "orderable": false },
              { "data" : "status", "orderable": false },
              { "data" : "current_peroids", "orderable": false },
          ],
          "order" : [],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证/订单号",
          },
          "ajax" : {
              "url":  "/operation/repay_loan_json",
              "data": function (d) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.query_str = $("#query_str").val();
                  d.query_type = $("#query_type").val();
                  d.query_strategy_type = $("#query_strategy_type").val();
                  d.channel = $("#channelBox").attr("name");
              }
          }
        },

        "table1" : {
          "columns": [
              { "name" : "channel", "orderable": true },
              { "name" : "order_no", "orderable": false },
              { "name" : "name", "orderable" : false },
              { "name" : "custom_type", "orderable" : false },
              { "name" : "card_id", "orderable": true },
              { "name" : "ammount", "orderable": true },
              { "name" : "corpus", "orderable": false },
              { "name" : "periods", "orderable": true },
              { "name" : "interest", "orderable": false },
              { "name" : "service_charge", "orderable": false },
              { "name" : "all_charge", "orderable": true },
              { "name" : "taikang_charge", "orderable": false },
              { "name" : "pay_day", "orderable": false },
          ],
          "order" : [],
          "ajax" : {
              "url":  "/operation/table1_json",
              "data": function (d) {
                  d.custom_type= $("#customeType").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },
        "table2" : {
           "aoColumnDefs": [
           // { "visible": false,  "targets": [1] }
           ],
          "columns": [
              { "name" : "peroids", "orderable": true },
              { "name" : "payinfo_number", "orderable": true },
              { "name" : "channel", "orderable": true },
              { "name" : "order_no", "orderable": false },
              { "name" : "name", "orderable" : false },
              { "name" : "custom_type", "orderable" : false },
              { "name" : "card_id", "orderable": true },
              { "name" : "ammount", "orderable": true },
              { "name" : "corpus", "orderable": false },
              { "name" : "periods", "orderable": true },
              { "name" : "interest", "orderable": false },
              { "name" : "all_charge", "orderable": true },
              { "name" : "taikang_charge", "orderable": false },
          ],
          "order" : [],
          "ajax" : {
              "url":  "/operation/table2_json",
              "data": function (d) {
                  d.time_range= $("#over_due_time_range").attr("name");
                  d.over_due_type= $("#over_due_type").attr("name");
                  d.custom_type= $("#customeType").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },

        "table3" : {
           "aoColumnDefs": [
           // { "visible": false,  "targets": [1] }
           ],
          "columns": [
              { "name" : "peroids", "orderable": true },
              { "name" : "order_number", "orderable": true },
              { "name" : "payinfo_number", "orderable": true },
              { "name" : "channel", "orderable": true },
              { "name" : "order_no", "orderable": false },
              { "name" : "name", "orderable" : false },
              { "name" : "custom_type", "orderable" : false },
              { "name" : "card_id", "orderable": true },
              { "name" : "ammount", "orderable": true },
              { "name" : "corpus", "orderable": false },
              { "name" : "periods", "orderable": true },
              { "name" : "interest", "orderable": false },
              { "name" : "all_charge", "orderable": true },
              { "name" : "taikang_charge", "orderable": false },
              { "name" : "taikang_charge12", "orderable": false },
          //    { "name" : "dd", "orderable": false },
          ],
          "order" : [],
          "ajax" : {
              "url":  "/operation/table3_json",
              "data": function (d) {
                  d.over_due_time_range= $("#over_due_time_range").attr("name");
                  d.over_due_type= $("#over_due_type").attr("name");
                  d.custom_type= $("#customeType").attr("name");
                  d.channel = $("#channelBox").attr("name");
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          }
        },



        "repay_loan_batch" : {
           "aoColumnDefs": [
            {
                "render": function ( data, type, row ) {
                    return '<input type="checkbox" '+ 'value =' + data  +  ' />' + data;
                },
                "targets": 0
            },
            { "visible": false,  "targets": [4,5,6] }
                    ],
          "columns": [
              { "data" : "id", "orderable": true },
              { "data" : "uid", "orderable": true },
              { "data" : "order_number", "orderable": false},
              { "data" : "name", "orderable": false},
              { "data" : "card_id", "orderable": false },
              { "data" : "amount", "orderable": true },
              { "data" : "repay_amount", "orderable": true },
              { "data" : "strategy", "orderable": false },
              { "data" : "bank_data", "orderable": true },
              { "data" : "apply_time", "orderable": true },
              { "data" : "getpay_time", "orderable": false },
              { "data" : "status", "orderable": false },
              { "data" : "current_peroids", "orderable": false },
          ],
          "order" : [],
          "ajax" : {
              "url":  "/operation/repay_loan_json",
              "data": function (d) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.query_str = $("#query_str").val();
                  d.query_type = $("#query_type").val();
                  d.query_status_type = 'batch_repay';
                  d.query_strategy_type = $("#query_strategy_type").val();
                  d.channel = $("#channelBox").attr("name");
              }
          }
        },

        "all_review" : {
           "aoColumnDefs": [
            { "visible": false,  "targets": [0] }
          ],
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "username", "orderable": true },
              { "name" : "type", "orderable": true },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "reviewer", "orderable": true },
              { "name" : "amount", "orderable": false },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"]],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证",
          },
          "ajax" : {
              "url":  "/review/all_review_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.status = $("#statusBox").attr("name");
                  d.type = $("#typeBox").attr("name");
                  d.time_filter = $("#timeFilterBox").attr("name");
                  d.channel = $("#channelBox").attr("name");
              }
          },
          "drawCallback": function () {
              //查看审批完成的信息
              $(".view_review").click(function(e) {
                  id = $(this).attr("name");
                  view_review_info(id, "#review_modal");
                  waitingDialog.show('加载中');
              });

              $(".view_second").click(function(e) {
                  view_loan_info($(this).attr("name"), "#review_modal");
                  waitingDialog.show('加载中');
              });

              $(".view_promote").click(function(e) {
                url = "/review/info/view/promote/" + $(this).attr("name");
                $("#review_modal").load(url, function(){
                  $(this).modal({backdrop: false});
                  //调整一下下对齐
                  $(this).on('shown.bs.modal', function() {
                      $('.review_right_panel').each(function() {
                          $(this).css('margin-top', $(this).parent().height()-$(this).height()-20);
                      });
                  });
                });
              });
           }
        },

        "my_review" : {
           "aoColumnDefs": [
            { "visible": false,  "targets": [0] }
          ],
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": true },
              { "name" : "username", "orderable": true },
              { "name" : "chsi_school", "orderable": true },
              { "name" : "id_no", "orderable": true },
              { "name" : "source", "orderable": true },
              { "name" : "create_at", "orderable": true },
              { "name" : "finish_time", "orderable": true },
              { "name" : "status", "orderable": false },
          ],
          "order" : [[0, "asc"]],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证",
          },
          "ajax" : {
              "url":  "/review/my_review_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
                  d.status = $("#statusBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
                  d.owner = $("#ownerBox").attr("name");
                  d.owner_id = $("#top_right_tools").attr("user_id");
              }
          },

          //加载完成后给按钮绑定
          "drawCallback": function () {



              //查看审批完成的信息
              $(".view_review").click(function(e) {
                  id = $(this).attr("name");
                  //waitingDialog.show('加载中');
                  view_review_info(id, "#review_modal");
              });

              $(".view_promote").click(function(e) {
                url = "/review/info/view/promote/" + $(this).attr("name");
                $("#review_modal").load(url, function(){
                  $(this).modal({backdrop: false});
                  //调整一下下对齐
                  $(this).on('shown.bs.modal', function() {
                      $('.review_right_panel').each(function() {
                          $(this).css('margin-top', $(this).parent().height()-$(this).height()-20);
                      });
                  });
                });
              });

              //额度提升
              $(".review_promote").click(function(e) {
                url = "/review/info/promote/" + $(this).attr("name");
                $("#review_modal").load(url, function(){
                  // 创建review，验证用户信息
                  $.ajax({
                      type : "POST",
                      url : "/review/action/add",
                      data : {"apply_id": $("#submit_promote").attr("apply_id")},
                      dataType : "json",
                      success:function(data, textstatus){
                          waitingDialog.hide();
                          if (data.error) {
                            alert(data.error);
                            $("#review_modal").modal('hide');
                          } else {
                            $("#review_modal").modal({backdrop: false});
                            //调整一下下对齐
                            $(this).on('shown.bs.modal', function() {
                                $('.review_right_panel').each(function() {
                                    $(this).css('margin-top', $(this).parent().height()-$(this).height()-20);
                                });
                            });

                            $("#submit_promote").click(function(e) {
                                $(this).button('loading');
                                $(this).prop('disabled', true);
                                var post_data = {'apply_id': $(this).attr("apply_id")};
                                post_data.score = $("#promotion_score").val();
                                post_data.apply_type = $(this).attr("apply_type");
                                $.ajax({
                                     type : "POST",
                                     url : "/review/action/promotion",
                                     data : post_data,
                                     dataType : "json",
                                     success:function(data, textstatus){
                                         $("#review_modal").modal('hide');
                                         $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                                     },
                                     error:function(a,textStatus,errorThrown){
                                         $("#review_modal").modal('hide');
                                         $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                                     }
                                });
                            });
                          }
                      },
                      error:function(a,textStatus,errorThrown){
                          alert('failed');
                      }
                  });
                });
              });

              $(".review_loan").click(function(e) {
                  load_loan_info($(this).attr("name"), "#review_modal");
                  waitingDialog.show('加载中');
              });

              $(".view_second").click(function(e) {
                  view_loan_info($(this).attr("name"), "#review_modal");
                  waitingDialog.show('加载中');
              });

              $(".review_manual").click(function(e) {
                  id = $(this).attr("name");
                  //setTimeout(function () {waitingDialog.hide();}, 2000);
                  load_review_info(id);
                  waitingDialog.show('加载中');
              });

              $(".review_auto").click(function(e) {
                url="/order/generate";
                id = $(this).attr("name");
                data= "type=review&applyid=" + id;
                $.ajax({
                  type:"GET",
                  url:url,
                  data:data,
                  error:function(a,textStatus,errorThrown){
                     alert('error! '+a.statusText+a.responseXML);
                  },
                  success:function(data, textstatus){
                      $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                  }
                });
              });
           }
        },

        "my_collection" : {
           "aoColumnDefs": [
            { "visible": false,  "targets": [0] }
          ],
          "columns": [
              { "name" : "id", "orderable" : true },
              { "name" : "uid", "orderable": false },
              { "name" : "username", "orderable": false },
              { "name" : "type", "orderable": true },
              { "name" : "strategy", "orderable": true },
              { "name" : "last_commit_at", "orderable": false },
              { "name" : "apply_amount", "orderable": true },
              { "name" : "overdue_amount", "orderable": true },
              { "name" : "reviewer", "orderable": false },
              { "name" : "status", "orderable": false }
          ],
          "order" : [[0, "desc"]],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证/订单/银行卡号",
          },
          "ajax" : {
              "url":  "/collection/my_collection_json",
              "data": function ( d ) {
                  d.owner_id = $("#top_right_tools").attr("user_id");
                  d.status = $("#statusBox").attr("name");
                  d.type = $("#typeBox").attr("name");
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          },
          "drawCallback": function () {
              //查看审批完成的信息
              $(".view_review").click(function(e) {
                  view_loan_info($(this).attr("name"), "#collection_modal");
                  waitingDialog.show('加载中');
              });

              $(".do_collection").click(function(e) {
                  do_collection($(this).attr("name"), "#collection_modal");
              });

              $(".view_collection").click(function(e) {
              });

              $(".dispatch_collection").click(function(e) {
                  waitingDialog.show('加载中');
                  do_dispatch_collection($(this).attr("name"), "#collection_modal");
              });
           }
        },

        "all_collection" : {
           "aoColumnDefs": [
            { "visible": false,  "targets": [0] }
          ],
          "columns": [
              { "name" : "id", "orderable" : false },
              { "name" : "uid", "orderable": false },
              { "name" : "username", "orderable": false },
              { "name" : "type", "orderable": false },
              { "name" : "repay_date", "orderable": true },
              { "name" : "overdue_days", "orderable": true },
              { "name" : "apply_amount", "orderable": true },
              { "name" : "reviewer", "orderable": false },
              { "name" : "status", "orderable": false },
              { "name" : "operaiont", "orderable": false }
          ],
          "language" :{
              "sSearchPlaceholder": "ID/姓名/手机/身份证/订单/银行卡号",
          },
          "order" : [[3, "desc"]],
          "ajax" : {
              "url": "/collection/all_collection_json",
              "data": function ( d ) {
                  d.status = $("#statusBox").attr("name");
                  d.type = $("#typeBox").attr("name");
                  d.time = $("#timeBox").attr("name");
                  d.stime = $("#timeBox").attr("stime");
                  d.etime = $("#timeBox").attr("etime");
              }
          },
          "drawCallback": function () {
              //查看审批完成的信息
              $(".view_review").click(function(e) {
                  view_loan_info($(this).attr("name"), "#collection_modal");
                  waitingDialog.show('加载中');
              });

              $(".do_collection").click(function(e) {
                  do_collection($(this).attr("name"), "#collection_modal");
              });

              $(".view_collection").click(function(e) {
              });

              $(".dispatch_collection").click(function(e) {
                  waitingDialog.show('加载中');
                  do_dispatch_collection($(this).attr("name"), "#collection_modal");
              });
           }
        },

        "all_feedback" : {
          "columns": [
              { "name" : "id", "orderable" : false },
              { "name" : "contact", "orderable": false },
              { "name" : "content", "orderable": false },
              { "name" : "sub_time", "orderable": true },
          ],
          "order" : [[0, "desc"],[3, "desc"]],
          "ajax" : {
              "url":  "/custom/get_feedback_json",
              "data": function ( d ) {
                  d.time = $("#timeBox").attr("name");
              }
          }
        },

        "all_record" : {
            "columns": [
                { "name" : "id", "orderable" : false },
                { "name" : "device", "orderable": false },
                { "name" : "version", "orderable": true },
                { "name" : "operation", "orderable": true },
                { "name" : "time", "orderable": true },
            ],
            "order" : [[0, "desc"],[3, "desc"]],
            "ajax" : {
                "url":  "/custom/get_record_json",
                "data": function ( d ) {
                    d.time = $("#timeBox").attr("name");
                }
            }
          },
        "user_info_record_table":{
          "serverSide": false,
          "lengthMenu" : [[8, 20, 50], ["8", "20", "50"]],
          "columns":[
              {"data": "add_staff"},
              {"data": "add_time"},
              //{"data": "promised_repay_time"},
              {"data": "notes"}
          ],
          //"order" : [[2, "desc"]],
          "ajax":{
              "url": "/order/get_user_info_note_data",
              "data": function (d){
                  d.user_id = $("#add_remark").attr('data-user-id');
              }
          }
        },


        "collection_record_table":{
          "serverSide": false,
          "lengthMenu" : [[8, 20, 50], ["8", "20", "50"]],
          "columns":[
              {"data": "record_type"},
              {"data": "collector"},
              {"data": "add_time"},
              //{"data": "promised_repay_time"},
              {"data": "notes"}
          ],
          "order" : [[2, "desc"]],
          "ajax":{
              "url": "/collection/get_collection_record_json",
              "data": function (d){
                  d.apply_id = $("#cancel_repayment").attr('aid');
                  d.record_type = $("#recordTypeBox").attr('name');
              }
          }
        },

        "loan_table":{
          "serverSide": false,
          "columns":[
              {"className": "details-control", "data":null, "orderable": false, "defaultContent": ''},
              {"data": "order_number"},
              {"data": "apply_amount"},
              {"data": "exact_amount"},
              {"data": "repay_status"},
              {"data": "apply_time"}
          ],
          "ajax":{
              "url": "/custom/get_loan_data",
              "data": function (d){
                  d.user_id = $("#user_info").attr('value');
              }
          }
        }
    };

    if ($("#all_order").length > 0) {
        var oTable = $('#all_order').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_order"]));
    } else if ($("#apply_order").length > 0) {
        var oTable = $('#apply_order').dataTable($.mergeJsonObject(baseSettings, datatable_param["apply_order"]));
    } else if ($("#promotion_order").length > 0) {
        var oTable = $('#promotion_order').dataTable($.mergeJsonObject(baseSettings, datatable_param["promotion_order"]));
    } else if ($("#loan_order").length > 0) {
        var oTable = $('#loan_order').dataTable($.mergeJsonObject(baseSettings, datatable_param["loan_order"]));
    } else if ($("#check_repay").length > 0) {
        var oTable = $('#check_repay').dataTable($.mergeJsonObject(baseSettings, datatable_param["check_repay"]));
    } else if ($("#all_review").length > 0) {
        var rTable = $('#all_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_review"]));

        $("#export_review_1").click(function(e) {
            time = $("#timeBox").attr("name");
            stime = $("#timeBox").attr("stime");
            etime = $("#timeBox").attr("etime");
            stat = $("#statusBox").attr("name");
            time_filter = $("#timeFilterBox").attr("name");
            $.fileDownload('/review/download_review_table_1?time=' + time + '&stime='+ stime + '&etime='+ etime + '&status='+ stat + '&time_filter=' + time_filter)
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });

        $("#export_review_2").click(function(e) {
            time = $("#timeBox").attr("name");
            stime = $("#timeBox").attr("stime");
            etime = $("#timeBox").attr("etime");
            stat = $("#statusBox").attr("name");
            type = $("#typeBox").attr("name");
            time_filter = $("#timeFilterBox").attr("name");
            $.fileDownload('/review/download_review_table_2?time=' + time + '&stime='+ stime + '&etime='+ etime + '&status='+ stat + '&time_filter=' + time_filter + "&type=" + type)
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });

        // 修改审批类型
        $("#typeBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#typeBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });

    } else if ($("#table1").length > 0) {
        var Table1 = $('#table1').dataTable($.mergeJsonObject(baseSettings, datatable_param["table1"]));
        $("#channelBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#customeType a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#customeType").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#export_table1").click(function(e) {
            $.fileDownload('/operation/download_table1?custom_type=' + $("#customeType").attr("name") + '&channel='+ $("#channelBox").attr("name") + '&time='+  $("#timeBox").attr("name") +  '&stime='+ $("#timeBox").attr("stime") + '&etime='+ $("#timeBox").attr("etime"))
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });
    } else if ($("#table2").length > 0) {
        var Table1 = $('#table2').dataTable($.mergeJsonObject(baseSettings, datatable_param["table2"]));
        $("#over_due_type a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#over_due_time_range a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#channelBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });

        $("#customeType a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#customeType").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
    } else if ($("#table3").length > 0) {
        var Table1 = $('#table3').dataTable($.mergeJsonObject(baseSettings, datatable_param["table3"]));
        $("#export_table3").click(function(e) {
            $.fileDownload('/operation/download_table3?'  +  "over_due_time_range=" + $("#over_due_time_range").attr("name") + "&over_due_type=" + $("#over_due_type").attr("name") +  "&channel=" +  $("#channelBox").attr("name") + "&time="  + $("#timeBox").attr("name")  +  "&stime="  +  encodeURI($("#timeBox").attr("stime"))  +  "&etime="  + encodeURI($("#timeBox").attr("etime")) + "&custom_type=" + $("#customeType").attr("name"))
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });
        $("#export_result").click(function(e) {
               // url = "/operation/table3_result/"; "&custom_type=" + $("#customeType").attr("name")
                url = "/operation/table3_result?" +  "over_due_time_range=" + $("#over_due_time_range").attr("name") + "&over_due_type=" + $("#over_due_type").attr("name") +  "&channel=" +  $("#channelBox").attr("name") + "&time="  + $("#timeBox").attr("name")  +  "&stime="  +  encodeURI($("#timeBox").attr("stime"))  +  "&etime="  + encodeURI($("#timeBox").attr("etime")) + "&custom_type=" + $("#customeType").attr("name");
                $('#result').on('hidden.bs.modal', function () {
                    //$("#pay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
                });
                $("#result").load(url, function(result){
//$("#pay_loan_mifan_account").dataTable($.mergeJsonObject(basemifanSettings, datatable_param["pay_loan_mifan_account"]));
                $(this).modal({backdrop: false});
                   // $("#table3").dataTable($.mergeJsonObject(basemifanSettings, datatable_param["table3"]));
                });
        });
        $("#over_due_time_range a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#over_due_time_range").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#over_due_type a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#over_due_type").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
        $("#channelBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });

        $("#customeType a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#customeType").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });
    } else if ($("#my_review").length > 0) {
        var rTable = $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
    } else if ($("#pay_loan").length > 0) {
        var pTable = $('#pay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));

        $('#pay_loan tbody').on( 'click', 'tr', function () {
           $(this).toggleClass('selected');
        });

        // 修改资金渠道
        $("#channelBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });


        $("#export_pay_loan").click(function(e) {
            if ($(".selected").length == 0) {
                alert("您没有选中任何行，请点击需要导出的数据，再点击导出名单");
            } else {
                d = [];
                $(".selected").each(function() {
                    d.push($(this).attr('id'));
                });
                //alert(d.join(','));
                $.fileDownload('/operation/download_pay_loan?type=' + $("#channelBox").attr("name") + '&aid='+ d.join(','))
                     .done(function () { alert('File download success!'); })
                     .fail(function () { alert('File download failed!'); });
            }
        });

        //======================自定义函数
        // 添加米饭打款查询接口
        $("#mifan_account_confirm").click(function(e) {
            basemifanSettings = {
                 "processing": true,
                 "serverSide": true,
                 "destroy": true,
                 "pagingType" : "full_numbers",
                 "autoWidth" : false,
                 "scrollCollapse": true,
                 "ordering": true,
                 "pageLength": 1000,
                 "lengthMenu" : [[15, 50, 100], ["15", "50", "100"]],
                 "language" : {
                   "processing" : "数据读取中...",
                   "lengthMenu" : "显示_MENU_条 ",
                   "zeroRecords" : "没有您要搜索的内容",
                   "info" : "从_START_ 到 _END_ 条记录 - 查询到的记录数为 _TOTAL_ 条",
                   "infoEmpty" : "记录数为0",
                   "infoFiltered" : "(全部记录数 _MAX_  条)",
                   "infoPostFix" : "",
                   "search" : "搜索",
                   "url" : "",
                   "paginate" : {
                       "first" : "第一页",
                       "previous" : " 上一页",
                       "next" : " 下一页 ",
                       "last" : "最后一页"
                  }
                }
            };
            url = "/operation/mifan_confirm_account/";
            $('#pay_modal').on('hidden.bs.modal', function () {
                $("#pay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
            });
            $("#pay_modal").load(url, function(result){
                $("#pay_loan_mifan_account").dataTable($.mergeJsonObject(basemifanSettings, datatable_param["pay_loan_mifan_account"]));
                $(this).modal({backdrop: false});
                $("#pay_loan_mifan_checkall").click(function() {
                    $("#pay_loan_mifan_account tbody tr input[type='checkbox']").each(function() {
                        //alert($(this).attr("checked"));
                        if($("#pay_loan_mifan_checkall").prop("checked"))
                        {
                            $(this).prop("checked", true);
                        }
                        else
                        {
                            $(this).prop("checked", false);
                        }
                    });
                  });



                  $('#mifan_account_submit_payment').click(function(e){
                      var  data = [];
                      $("#pay_loan_mifan_account tbody tr input[type='checkbox']").each(function() {
                          if($(this).is(':checked'))
                          {
                                $(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-refresh");
                                data.push($(this).val());
                          }
                      });
                     jsondata = JSON.stringify(data);
                      $.ajax({
                          type:"GET",
                          url:"/operation/mifan_account_confirm_idlist",
                          data: {"id_list":jsondata, 'token': $(this).attr("token")},
                          dataType:'json',
                          success:function(data){
                               if(data["error"] == "不能重复提交"){
                                           alert('不能重复提交');
                                           return ;
                               }
                               $("#pay_loan_mifan_account tbody tr input[type='checkbox']").each(function() {
                                        if($(this).is(':checked')){
                                        var test = $(this).parent().parent();
                                        //alert($(this).parent().parent().find('td:last-child').text());
                                            // 清空原来的米饭打款状态码
                                            $(this).parent().parent().find('td:last-child').text("");
                                            //$(this).parent().parent().find('td:last-child').empty();
                                            if(data[$(this).val()] == "已到账" || data[$(this).val()] == "已经放款"){
                                                $(this).parent().parent().find('td:last-child').append(data[$(this).val() + 'errorCode']);
                                                $(this).parent().parent().find('td:last-child').removeClass();
                                                $(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-ok");
                                            }
                                            else {
                                                 console.log(data[$(this).val() + 'errorCode']);
                                                 $(this).parent().parent().find('td:last-child').append(data[$(this).val() + 'errorCode']);
                                                 $(this).parent().parent().find('td:last-child').removeClass();
                                                 $(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-remove");}
                                                 $(this).parent().parent().find('td:last-child').tooltip({
                                                            trigger:'hover',
                                                            html:true,
                                                            title:data[$(this).val()]})
                                                  }
                                                 });
                        },
                          error:function(a,textStatus,errorThrown){
                             alert('error! '+a.statusText+a.responseXML);
                          }
                      });
                  });

                });
                     // $.ajax({
                     //     type:"GET",
                     //     url:"/operation/mifan_account_confirm_idlist",
                     //     dataType:'json',
                     //     success:function(data){
                     //       alert(data);
		     //   }
                     //   });
        });

        $("#export_pay_loan_table").click(function(e) {
            $.fileDownload('/operation/export_pay_loan_table?'  +    "&channel=" +  $("#channelBox").attr("name") + "&time="  + $("#timeBox").attr("name")  +  "&stime="  +  encodeURI($("#timeBox").attr("stime"))  +  "&etime="  + encodeURI($("#timeBox").attr("etime")) + "&query_type=" + $("#query_type").val()  +  "&status=" +  $("#statusBox").attr("name") + "&query_str=" + $("#query_str").val() + "&query_strategy_type=" + $("#query_strategy_type").val())
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });
        $("#query_pay_apply").click(function(e) {
              $("#pay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
        });
        //======================自定义函数
        // 添加米饭确认打款接口
        $("#mifan_confirm").click(function(e) {
            if( $("#statusBox").attr("name") == "prepayed"  || $("#statusBox").attr("name") == "success" || $("#statusBox").attr("name") == "failed" )
            {    alert("请选择状态为等待放款的单子");return;
            }
            basemifanSettings = {
                 "processing": true,
                 "serverSide": true,
                 "destroy": true,
                 "pagingType" : "full_numbers",
                 "autoWidth" : false,
                 "scrollCollapse": true,
                 "ordering": true,
                 "pageLength": 1000,
                 "lengthMenu" : [[15, 50, 100], ["15", "50", "100"]],
                 "language" : {
                   "processing" : "数据读取中...",
                   "lengthMenu" : "显示_MENU_条 ",
                   "zeroRecords" : "没有您要搜索的内容",
                   "info" : "从_START_ 到 _END_ 条记录 - 查询到的记录数为 _TOTAL_ 条",
                   "infoEmpty" : "记录数为0",
                   "infoFiltered" : "(全部记录数 _MAX_  条)",
                   "infoPostFix" : "",
                   "search" : "搜索",
                   "url" : "",
                   "paginate" : {
                       "first" : "第一页",
                       "previous" : " 上一页",
                       "next" : " 下一页 ",
                       "last" : "最后一页"
                  }
                }
            };
            url = "/operation/mifan_confirm/";
            $('#pay_modal').on('hidden.bs.modal', function () {
                $("#pay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
            });
            $("#pay_modal").load(url, function(result){
                $("#pay_loan_mifan").dataTable($.mergeJsonObject(basemifanSettings, datatable_param["pay_loan_mifan"]));
                $(this).modal({backdrop: false});
                $("#pay_loan_mifan_checkall").click(function() {
                    $("#pay_loan_mifan tbody tr input[type='checkbox']").each(function() {
                        //alert($(this).attr("checked"));
                        if($("#pay_loan_mifan_checkall").prop("checked"))
                        {
                            $(this).prop("checked", true);
                        }
                        else
                        {
                            $(this).prop("checked", false);
                        }
                    });
                });
                  $('#mifan_submit_payment').click(function(e){
                      var  data = [];
                      $("#pay_loan_mifan tbody tr input[type='checkbox']").each(function() {
                          if($(this).is(':checked'))
                          {
                                //$(this).prev().css("color","#ff9955");
                                $(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-refresh");
                                //$(this).prev().addClass("glyphicon glyphicon-refresh");
                                //$(this).prev().css("class","glyphicon glyphicon-refresh");
 				data.push($(this).val());
			  }
 		      });
                     jsondata = JSON.stringify(data);
 		     //alert(jsondata);
                      $.ajax({
                          type:"GET",
                          url:"/operation/mifan_confirm_idlist",
                          data: {"id_list":jsondata , 'token': $(this).attr("token")},
                          dataType:'json',
                          success:function(data){
                               if(data["error"] == "不能重复提交"){
                                               alert('不能重复提交');
                                               return ;
                               }
                               if(data["error"] == "mifan failed"){
                                               alert('批量处理米饭代付时出现异常,本次处理可能有些代付过程没有发送成功,联系一下后台人员确认下');
                               }
                               $("#pay_loan_mifan tbody tr input[type='checkbox']").each(function() {
                                        if($(this).is(':checked')){
        				var test = $(this).parent().parent();
        				//alert($(this).parent().parent().find('td:last-child').text());
 				            // 清空原来的米饭打款状态码
                                            $(this).parent().parent().find('td:last-child').text("");
                                            //$(this).parent().parent().find('td:last-child').empty();
                                            if(data[$(this).val()] == "success"){
                                                $(this).parent().parent().find('td:last-child').append(data[$(this).val() + 'errorCode']);
						$(this).parent().parent().find('td:last-child').removeClass();
						$(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-ok");
   					    }
                                            else {
                                                 console.log(data[$(this).val() + 'errorCode']);
                                                 $(this).parent().parent().find('td:last-child').append(data[$(this).val() + 'errorCode']);
						 $(this).parent().parent().find('td:last-child').removeClass();
						 $(this).parent().parent().find('td:last-child').addClass("glyphicon glyphicon-remove");}
                                                 $(this).parent().parent().find('td:last-child').tooltip({
  						            trigger:'hover',
  						            html:true,
  						            title:data[$(this).val()]})
  						  }
  						 });
  			},
                          error:function(a,textStatus,errorThrown){
                             alert('error! '+a.statusText+a.responseXML);
                          }
                      });
                  });
            })
        });


        $("#do_pay_done").click(function(e) {
            //    alert("ok");
            if ($(".selected").length === 0) {
                alert("您没有选中任何行，请点击需要确认的，再点击确认打款，暂时只支持单条记录");
            } else {
                d = [];
                $(".selected").each(function() {
                    d.push($(this).attr('id'));
                });
                //alert(d.join(','));
                if (d.length != 1)  {
                    alert("确认打款仅支持一条记录");
                } else {
                    url = "/operation/pay_modal/" + d[0];
                    $("#pay_modal").load(url, function(){
                        $(this).modal({backdrop: false});
                        $.ajax({
                            type:"GET",
                            url:url,
                            error:function(a,textStatus,errorThrown){
                               alert('error! '+a.statusText+a.responseXML);
                            },
                            success:function(data, textstatus){
                                $('#submit_payment').click(function(e){
                                    $(this).button('loading');
                                    $(this).prop('disabled', true);
                                    $.ajax({
                                        type:"GET",
                                        url:"/operation/do_pay_loan",
                                        data: { 'type':'realtime_pay','aid': $(this).attr("aid")},
                                        dataType:'json',
                                        success:function(data, textstatus){
                                            $('#pay_modal').hide();
                                            alert(data.msg);
                                        },
                                        error:function(a,textStatus,errorThrown){
                                           alert('error! '+a.statusText+a.responseXML);
                                        }
                                    });
                                });
                                $('#submit_payment_success').click(function(e){
                                    $(this).button('loading');
                                    $(this).prop('disabled', true);
                                    $.ajax({
                                        type:"GET",
                                        url:"/operation/do_pay_loan",
                                        data: { 'type':'comfirm_success', 'aid': $(this).attr("aid")},
                                        dataType:'json',
                                        success:function(data, textstatus){
                                            $('#pay_modal').modal('hide');
                                            $('#pay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
                                        },
                                        error:function(a,textStatus,errorThrown){
                                            alert('error! '+a.statusText+a.responseXML);
                                            $('#pay_modal').modal('hide');
                                        }
                                    });
                                });
                                $('#submit_payment_failed').click(function(e){
                                    $(this).button('loading');
                                    $(this).prop('disabled', true);
                                    $.ajax({
                                        type:"GET",
                                        url:"/operation/do_pay_loan",
                                        data: { 'type':'comfirm_failed', 'aid': $(this).attr("aid")},
                                        dataType:'json',
                                        success:function(data, textstatus){
                                            $('#pay_modal').modal('hide');
                                            $('#pay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["pay_loan"]));
                                        },
                                        error:function(a,textStatus,errorThrown){
                                            alert('error! '+a.statusText+a.responseXML);
                                            $('#pay_modal').modal('hide');
                                        }
                                    });
                                });
                            }
                        });
                    });
                }
            }
        });

    } else if ($("#repay_loan").length > 0) {
        var pTable = $('#repay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
        // 修改资金渠道
        $("#channelBox a").click(function(e) {
            $(this).siblings().removeClass("btn-primary");
            $(this).siblings().removeClass("btn-default");
            $(this).siblings().addClass("btn-default");
            $(this).addClass("btn-primary");
            $("#channelBox").attr("name", $(this).attr("name"));
            //刷新表单数据
            table = $(this).parent().siblings(".boxA").find("table");
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        });

        $('#repay_loan tbody').on( 'click', 'tr', function () {
           $(this).toggleClass('selected');
        });

        $("#export_repay_loan_table").click(function(e) {
            $.fileDownload('/operation/export_repay_loan_table?'  +    "&channel=" +  $("#channelBox").attr("name") + "&time="  + $("#timeBox").attr("name")  +  "&stime="  +  encodeURI($("#timeBox").attr("stime"))  +  "&etime="  + encodeURI($("#timeBox").attr("etime")) + "&query_type=" + $("#query_type").val()  +  "&status=" +  $("#statusBox").attr("name") + "&query_str=" + $("#query_str").val() + "&query_strategy_type=" + $("#query_strategy_type").val())
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });


        $("#do_repay_loan_batch").click(function(e) {
            if ($("#statusBox").attr("name") == "repay_success")
            {
               alert("所选类别已经扣款成功，请选择其他类别");
               return;
            }
            $('#pay_modal_batch').on('hidden.bs.modal', function () {
                $("#repay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
            });
             url = "/operation/repay_modal_batch/";
             $("#repay_modal").load(url, function(){
                  $("#repay_loan_batch_table").dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan_batch"]));
                  $(this).modal({backdrop: false});
                  $("#repay_loan_batch_checkall").click(function() {
                    $("#repay_loan_batch_table tbody tr input[type='checkbox']").each(function() {
                        if($("#repay_loan_batch_checkall").prop("checked"))
                        {
                            $(this).prop("checked", true);
                        }
                        else
                        {
                            $(this).prop("checked", false);
                        }
                    });
                });
                 $('#repay_batch_submit').click(function(e){
                      var  data = [];
                      $("#repay_loan_batch_table tbody tr input[type='checkbox']").each(function() {
                          if($(this).is(':checked'))
                          {
                                data.push($(this).val());
                          }
                      });
                      jsondata = JSON.stringify(data);
                      $.ajax({
                          type:"GET",
                          url:"/operation/repay_batch_idlist",
                          data: {"id_list":jsondata, 'token': $(this).attr("token")},
                          dataType:'json',
                          success:function(data){
                                    if(data["error"] == "不能重复提交"){
                                                alert('不能重复提交');
                                                return ;
                                    }
                                    $("#repay_loan_batch_table tbody tr input[type='checkbox']").each(function() {
                                          if($(this).is(':checked')){
                                            if(data[$(this).val()] == "扣款成功"){
                                                $(this).parent().parent().find('td:first-child').addClass("glyphicon glyphicon-ok");
                                            }
                                            else {
                                                 $(this).parent().parent().find('td:first-child').addClass("glyphicon glyphicon-remove");
   					    }
                                             $(this).parent().parent().find('td:first-child').tooltip({
  						            trigger:'hover',
  						            html:true,
  					//	            title:'dd'})
  						            title:data[$(this).val()]})
  				          }
                                     });
                          },
                          error:function(a,textStatus,errorThrown){
                             alert('error! '+a.statusText+a.responseXML);
                          }
                      });
                 });
             });
        });

        $("#query_repay_apply").click(function(e) {
              $("#repay_loan").dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
        });


        $("#do_repay_loan").click(function(e) {
            if ($(".selected").length === 0) {
                alert("您没有选中任何行，请点击需要确认的，再点击确认扣款，暂时只支持单条记录");
            } else {
                if ($("#statusBox").attr("name") == "repay_success")
                {
                   alert("所选类别已经扣款成功，请选择其他类别");
                   return;
                }
                d = [];
                $(".selected").each(function() {
                    d.push($(this).attr("id"));
                });
                if (d.length != 1)  {
                    alert("扣款仅支持一条记录");
                } else {
                    url = "/operation/repay_modal/" + d[0];
                    $("#repay_modal").load(url, function() {
                        $(this).modal({backdrop: false});
                        $("#check_file").fileinput({
                            uploadUrl : "/collection/action/fileupload",
                        });

                        $('#check_file').on('fileuploaded', function(event, data, previewId, index) {
                            var form = data.form, files = data.files, extra = data.extra,
                                response = data.response, reader = data.reader;
                            console.log('File uploaded triggered');
                            //alert(response.url);
                            $('#check_file').attr("url", response.url);
                        });

                        $.ajax({
                            type:"GET",
                            url:url,
                            error:function(a,textStatus,errorThrown){
                               alert('error! '+a.statusText+a.responseXML);
                            },
                            success:function(data, textstatus){
                                $('#submit_collection_record').click(function(e){
                                    if ($(this).attr("aid") != "null") {
                                        add_collection_record_from_repay( $(this).attr("aid"), "#collection_record_table");
                                    }
                                });

                                load_repay_buttom();
  				load_colletion_record_table();
                                $('#submit_repayment').click(function(e){
                                    //$(this).button('loading');
                                    //$(this).prop('disabled', true);
                                    submit_data = {'aid': $(this).attr("aid"), 'token': $(this).attr("token")};
                                    submit_data["channel"] = $("#repay_channel_radiobox").find('input[name="repay_channel"]:checked').val();
                                    submit_data["type"] = $("#repay_type_radiobox").find('input[name="repay_type"]:checked').val();
                                    submit_data["url"] = $("#check_file").attr("url");
                                    submit_data["notes"] = $("#check_notes").val();
                                    submit_data["check_amount"] = $("#check_amount").val();
                                    if(submit_data["type"] === "custom") {
                                        submit_data["amount"] = $("#repay_amount_input").val();
                                    } else {
                                        submit_data["amount"] = $("#repay_type_" + submit_data["type"]).attr("amount");
                                    }
                                    //alert(submit_data["notes"], submit_data["check_amount"], submit_data["url"]);
                                    $.ajax({
                                        type:"GET",
                                        url:"/operation/do_repay_loan",
                                        data: submit_data,
                                        dataType:'json',
                                        success:function(data, textstatus){
                                            if (data.error == 'ok') {
                                                $('#repay_modal').modal("hide");
                                                //alert(data.msg);
                                            } else {
                                                alert(data.msg);
                                            }
                                            $('#repay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
                                        },
                                        error:function(a,textStatus,errorThrown){
                                           alert('error! '+a.statusText+a.responseXML);
                                        }
                                    });
                                });

                                load_loan_table();
//  				load_colletion_record_table();
                            }
                        });
                    });
                }
            }
        });

        $("#do_repay_loan4custom").click(function(e) {
            if ($(".selected").length === 0) {
                alert("您没有选中任何行，请点击需要确认的，再点击确认扣款，暂时只支持单条记录");
            } else {
                if ($("#statusBox").attr("name") == "repay_success")
                {
                   alert("所选类别已经扣款成功，请选择其他类别");
                   return;
                }
                d = [];
                $(".selected").each(function() {
                    d.push($(this).find("td:first").html());
                });
                if (d.length != 1)  {
                    alert("扣款仅支持一条记录");
                } else {
                    url = "/operation/repay_modal4custom/" + d[0];
                    $("#repay_modal").load(url, function() {
                        $(this).modal({backdrop: false});
                        $("#check_file").fileinput({
                            uploadUrl : "/collection/action/fileupload",
                        });

                        $('#check_file').on('fileuploaded', function(event, data, previewId, index) {
                            var form = data.form, files = data.files, extra = data.extra,
                                response = data.response, reader = data.reader;
                            console.log('File uploaded triggered');
                            //alert(response.url);
                            $('#check_file').attr("url", response.url);
                        });

                        $.ajax({
                            type:"GET",
                            url:url,
                            error:function(a,textStatus,errorThrown){
                               alert('error! '+a.statusText+a.responseXML);
                            },
                            success:function(data, textstatus){
                                $('#submit_collection_record').click(function(e){
                                    if ($(this).attr("aid") != "null") {
                                        add_collection_record_from_repay( $(this).attr("aid"), "#collection_record_table");
                                    }
                                });

                                load_repay_buttom();

                                $('#submit_repayment').click(function(e){
                                    //$(this).button('loading');
                                    //$(this).prop('disabled', true);
                                    submit_data = {'aid': $(this).attr("aid"), 'token': $(this).attr("token")};
                                    submit_data["channel"] = $("#repay_channel_radiobox").find('input[name="repay_channel"]:checked').val();
                                    submit_data["type"] = $("#repay_type_radiobox").find('input[name="repay_type"]:checked').val();
                                    submit_data["url"] = $("#check_file").attr("url");
                                    submit_data["notes"] = $("#check_notes").val();
                                    submit_data["check_amount"] = $("#check_amount").val();
                                    if(submit_data["type"] === "custom") {
                                        submit_data["amount"] = $("#repay_amount_input").val();
                                    } else {
                                        submit_data["amount"] = $("#repay_type_" + submit_data["type"]).attr("amount");
                                    }
                                    //alert(submit_data["notes"], submit_data["check_amount"], submit_data["url"]);
                                    $.ajax({
                                        type:"GET",
                                        url:"/operation/do_repay_loan",
                                        data: submit_data,
                                        dataType:'json',
                                        success:function(data, textstatus){
                                            if (data.error == 'ok') {
                                                $('#repay_modal').modal("hide");
                                                //alert(data.msg);
                                            } else {
                                                alert(data.msg);
                                            }
                                            $('#repay_loan').dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
                                        },
                                        error:function(a,textStatus,errorThrown){
                                           alert('error! '+a.statusText+a.responseXML);
                                        }
                                    });
                                });

                                load_loan_table();
                            }
                        });
                    });
                }
            }
        });

    } else if ($("#my_collection").length > 0) {
        $('#my_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param.my_collection));
    } else if ($("#all_collection").length > 0) {
        $('#all_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param.all_collection));

        $("#export_collection_1").click(function(e) {
            time = $("#timeBox").attr("name");
            stime = $("#timeBox").attr("stime");
            etime = $("#timeBox").attr("etime");
            stat = $("#statusBox").attr("name");
            type = $("#typeBox").attr("name");
            time_filter = $("#timeFilterBox").attr("name");
            $.fileDownload('/collection/download_collection_table_1?time=' + time + '&stime='+ stime + '&etime='+ etime + '&status='+ stat + '&time_filter=' + time_filter + '&type=' + type)
                 .done(function () { alert('File download success!'); })
                 .fail(function () { alert('File download failed!'); });
        });

    } else if ($("#all_feedback").length > 0) {
        $('#all_feedback').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_feedback"]));
    }  else if ($("#all_record").length > 0) {
        $('#all_record').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_record"]));
    } else if ($("#user_info_display").length > 0) {
        load_user_info();
    }
    //alert(JSON.stringify(baseSettings));


    //setInterval( function () {
    //    oTable.ajax.reload(null, false);
    //}, 5000 );
    //开始审批按钮
    $("#start_review").click(function(e) {
        name = $(this).attr("name");
        if (name == "offline") {
            $(this).attr("name", "online");
            $(this).text("停止审批");
        } else if (name == "online") {
            $(this).attr("name", "offline");
            $(this).text("开始审批");
        }
    });


    // 测试按钮
    $("#gen_order").click(function(e) {
        url="/order/generate";
        data= "type=baseapply";
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textstatus){
              alert("ok");
          }
        });
    });

    $("#gen_promotion").click(function(e) {
        url="/order/generate";
        data= "type=promotion";
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textstatus){
              alert("ok");
          }
        });
    });

    $("#clear_today_order").click(function(e) {
        url="/order/clear";
        data= "&type=apply&timerange=today";
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textStatus){
              alert("OK");
          }
        });
    });

    $("#clear_all_order").click(function(e){
        url="/order/clear";
        data= "type=apply&timerange=all";
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textStatus){
              alert("OK");
          }
        });
    });

    // 修改时间范围
    $("#timeBox>a").click(function(e) {
        $(this).siblings().removeClass("btn-primary");
        $(this).siblings().removeClass("btn-default");
        $(this).siblings().addClass("btn-default");
        $(this).addClass("btn-primary");
        $("#timeBox").attr("name", $(this).attr("name"));
        //刷新表单数据
        table = $(this).parent().siblings(".boxA").find("table");
        if ($(this).attr("name") !== "custom") {
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        }
    });

    $("#timeBox a[name='custom']").daterangepicker(
        {
            "timePicker": true,
            "timePicker24Hour": true,
            "autoApply": true,
            "opens": "left",
            //"drops": "down",
            "locale": {
                "format": "MM/DD/YYYY",
                "separator": " - ",
                "applyLabel": "确定",
                "cancelLabel": "取消",
                "fromLabel": "从",
                "toLabel": "到",
                "customRangeLabel": "自定义",
                "daysOfWeek": [
                    "日",
                    "一",
                    "二",
                    "三",
                    "四",
                    "五",
                    "六"
                ],
                "monthNames": [
                    "一月",
                    "二月",
                    "三月",
                    "四月",
                    "五月",
                    "六月",
                    "七月",
                    "八月",
                    "九月",
                    "十月",
                    "十一月",
                    "十二月"
                ],
                "firstDay": 1
            }
            //startDate: '2013-01-01',
            //endDate: '2013-12-31'
        },
        function(start, end, label) {
            //alert('A date range was chosen: ' + start.format('YYYY-MM-DD hh:mm') + ' to ' + end.format('YYYY-MM-DD hh:mm'));
            $("#timeBox").attr("stime", start.format('YYYY-MM-DD HH:mm:ss'));
            $("#timeBox").attr("etime", end.format('YYYY-MM-DD HH:mm:ss'));
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        }
    );


    // 修改订单状态
    $("#statusBox a").click(function(e) {
        $(this).siblings().removeClass("btn-primary");
        $(this).siblings().removeClass("btn-default");
        $(this).siblings().addClass("btn-default");
        $(this).addClass("btn-primary");
        $("#statusBox").attr("name", $(this).attr("name"));
        //刷新表单数据
        table = $(this).parent().siblings(".boxA").find("table");
        table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
    });

    // 修改订单状态
    $("#typeBox a").click(function(e) {
        $(this).siblings().removeClass("btn-primary");
        $(this).siblings().removeClass("btn-default");
        $(this).siblings().addClass("btn-default");
        $(this).addClass("btn-primary");
        $("#typeBox").attr("name", $(this).attr("name"));
        //刷新表单数据
        table = $(this).parent().siblings(".boxA").find("table");
        table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
    });

    // 修改订单状态
    $("#timeFilterBox a").click(function(e) {
        $("#timeFilterBox").attr("name", $(this).attr("name"));
        //刷新表单数据
        table = $("#timeFilterBox").parent().parent().siblings(".boxA").find("table");
        table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
    });


    // 修改催记类型
    $("#recordTypeBox a").click(function(e) {
        $("#recordTypeBox").attr("name", $(this).attr("name"));
        table = $("#collection_record_table");
        $("#recordTypeButton").html($(this).text() + '<span class="caret">');
        //刷新表单数据
        table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
    });

    // 修改归属
    $("#ownerBox a").click(function(e) {
        $(this).siblings().removeClass("btn-primary");
        $(this).siblings().removeClass("btn-default");
        $(this).siblings().addClass("btn-default");
        $(this).addClass("btn-primary");
        $("#ownerBox").attr("name", $(this).attr("name"));
        //刷新表单数据
        table = $(this).parent().siblings(".boxA").find("table");
        if ($(this).attr("name") !== "custom") {
            table.dataTable($.mergeJsonObject(baseSettings, datatable_param[table.attr("id")]));
        }
    });

    //结清贷款
    $("#repay_repayment").click(function(e) {
        url = "/order/clear";
        alert(url);
        order_number = $("#repay_repayment_input").val();
        data= "&type=loan&order_number="+ order_number;
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textStatus){
              alert("OK");
          }
        });
    });

    //删除用户
    $("#delete_user").click(function(e){
        url = "/order/clear";
        phone_no = $("#delete_user_input").val();
        alert(phone_no);
        data= "&type=user&phone_no="+ phone_no;
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textStatus){
              alert("OK");
          }
        });
    });

    //查询
    $("#query_user").click(function(e){
        query_str = $("#query_str").val();
        url = "/custom/query/";
        data = "&query_str=" + query_str;
        $.ajax({
          type:"GET",
          url:url,
          data:data,
          error:function(a,textStatus,errorThrown){
              alert('error! '+a.statusText+a.responseXML);
          },
          success:function(data, textStatus){
              document.getElementById("query_result").innerHTML = data;
              load_user_info();
              $('#user_info_note_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["user_info_record_table"]));
                      $("#add_remark").click(function(e) {
                          url = "/custom/addremark/";
                          data = "content=" + $("#user_info_record").val() + "&user_id=" + $(this).data('user-id');
                          $.ajax({
                            type:"GET",
                            url:url,
                            data:data,
                            error:function(a,textStatus,errorThrown){
                                alert('error! '+a.statusText+a.responseXML);
                            },
                            success:function(data, textStatus){
                                var obj = $.parseJSON(data);
                                alert(obj.result);
                                $('#user_info_note_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["user_info_record_table"]));
                            },
                          })
                      });


                      $("#sendmessage").click(function(e) {
                               $.ajax({
                                   type:"POST",
                                   url:"/custom/send_message/",
                                   data: { 'phone_no': $("#phone_no_to_send").val(),'content': $("#content_to_send").val()},
                                   dataType:'json',
                                   success:function(data, textstatus){
                                       if (data.error) {
                                           alert(data.error);
                                       } else {
                                           alert('发送短信成功');
                                       }
                                   },
                                   error:function(a,textStatus,errorThrown){
                                       alert("系统错误 短信发送失败");
                                       //alert('error! '+a.statusText+a.responseXML);
                                   }
                               });

                      });
//              var user_id = "";
//              $('#add_remark_Modal').on('show.bs.modal', function(e) {
//               	  user_id = $(e.relatedTarget).data('user-id');
//              });

              $(".query_user_detail").click(function(e){
                url = "/custom/query_detail/";
                data = "&query_user_id=" + $(this).attr("name");
                $.ajax({
                  type:"GET",
                  url:url,
                  data:data,
                  error:function(a,textStatus,errorThrown){
                      alert('error! '+a.statusText+a.responseXML);
                  },
                  success:function(data, textStatus){
                      document.getElementById("user_detail").innerHTML = data;
                      load_user_info();
                      $('#user_info_note_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["user_info_record_table"]));
                      $("#add_remark").click(function(e) {
                          url = "/custom/addremark/";
                          data = "content=" + $("#user_info_record").val() + "&user_id=" + $(this).data('user-id');
                          $.ajax({
                            type:"GET",
                            url:url,
                            data:data,
                            error:function(a,textStatus,errorThrown){
                                alert('error! '+a.statusText+a.responseXML);
                            },
                            success:function(data, textStatus){
                                var obj = $.parseJSON(data);
                                alert(obj.result);
                                $('#user_info_note_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["user_info_record_table"]));
                            },
                          })
                      });


                      $("#sendmessage").click(function(e) {
                               $.ajax({
                                   type:"POST",
                                   url:"/custom/send_message/",
                                   data: { 'phone_no': $("#phone_no_to_send").val(),'content': $("#content_to_send").val()},
                                   dataType:'json',
                                   success:function(data, textstatus){
                                       if (data.error) {
                                           alert(data.error);
                                       } else {
                                           alert('发送短信成功');
                                       }
                                   },
                                   error:function(a,textStatus,errorThrown){
                                       alert("系统错误 短信发送失败");
                                       //alert('error! '+a.statusText+a.responseXML);
                                   }
                               });

                      });

                  }
                });
              });
          }
        });
    });
});


function load_user_info() {
    if ($("#user_info").length > 0) {
        user_id = $("#user_info").attr('value');
        $("#get_user_detail").click(function(e){
            var n = document.getElementById("user_info_detail");
            if(n.style.display == "none"){
                n.style.display = "block";
                this.textContent = "收起";
            }else{
                n.style.display = "none";
                this.textContent = "展开";
            }
        });
        load_loan_table();
    }
}

function loan_detail_format(d) {
    new_row = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">' +
              '<tr>' +
              '<th>期号</th>' +
              '<th>应还日期</th>' +
              '<th>实际还款日期</th>' +
              '<th>应还金额</th>' +
              '<th>已还金额</th>' +
              '<th>还款状态</th>' +
              '<th>生成代扣订单</th>' +
              '<th>逾期天数</th>' +
              '<th>逾期状态</th>' +
              '<th>贷款期限</th>' +
              '<th>滞纳金</th>' +
              '<th>未还金额</th>' +
              '<th>催收人</th>' +
              '</tr>';

    for(var o in d.install_list){
        temp_str = '<tr>' +
                  '<td>' + d.install_list[o].installment_number + '</td>' +
                  '<td>' + d.install_list[o].should_repay_time + '</td>' +
                  '<td>' + d.install_list[o].real_repay_time + '</td>' +
                  '<td>' + d.install_list[o].should_repay_amount + '</td>' +
                  '<td>' + d.install_list[o].real_repay_amount + '</td>' +
                  '<td>' + d.install_list[o].repay_status + '</td>' +
                  '<td>' + d.install_list[o].repay_apply+ '</td>' +
                  '<td>' + d.install_list[o].over_due_days+ '</td>' +
                  '<td>' + d.install_list[o].over_due_status+ '</td>' +
                  '<td>' + d.install_list[o].stratety_type+ '</td>' +
                  '<td>' + d.install_list[o].over_due_repay+ '</td>' +
                  '<td>' + d.install_list[o].should_repay+ '</td>' +
                  '<td>' + d.install_list[o].review_staff_name+ '</td>' +
                  '</tr>'
        new_row = new_row + temp_str
    }
    return new_row + '</table>'
}

//function load_basic_info() {
//
//
//}

//load 催收 modal
function load_collection_info(id) {
    url = "/collection/info/" + id;
    $("#collection_modal").load(url, function(){
        $.ajax({
            type : "POST",
            url : "/review/action/add",
            data : {"apply_id": $("#submit_loan").attr("apply_id")},
            dataType : "json",
            success:function(data, textstatus) {
                if (data.error) {
                    alert(data.error);
                    $("#collection_modal").modal('hide');
                } else {
                    $("#collection_modal").modal({backdrop: false});
                    load_loan_table();
                    $("#submit_collection").click(function(e) {
                        do_submit_collecotion();
                    });
                }
            },
            error:function(a,textStatus,errorThrown) {
                alert('failed');
            }
        });
    });
}

function do_submit_collecotion() {

}

function load_loan_info(id, modal_name) {
    url = "/review/info/loan/" + id;
    //alert(url);
    $(modal_name).load(url, function(){
        // 创建review，验证用户信息
        $.ajax({
            type : "POST",
            url : "/review/action/add",
            data : {"apply_id": $("#submit_loan").attr("apply_id")},
            dataType : "json",
            success:function(data, textstatus) {
                waitingDialog.hide();
                if (data.error) {
                    alert(data.error);
                    $(modal_name).modal('hide');
                } else {
                    $(modal_name).modal({backdrop: false});
                    //调整一下下对齐
                    $(this).on('shown.bs.modal', function() {
                        $('.review_right_panel').each(function() {
                            $(this).css('margin-top', $(this).parent().height()-$(this).height()-20)
                        });
                    });

                    load_loan_table();

                    $("#submit_loan").click(function(e) {
                        var post_data = {'apply_id': $(this).attr("apply_id")};
                        name = "total_area";
                        post_data[name+"_notes"]= $("#total_area_section").find(".notes_area").val();
                        post_data[name+"_msg"]= $("#total_area_section").find(".msg_area").val();
                        post_data[name+"_radio"]= $("#total_area_section").find("input[name=" + name + "]:checked").val();
                        res = $("#total_area_section").find("input[name=" + name + "]:checked").val();

                        if (res === 'y') {
                            res = "通过";
                        } else if (res === 'r') {
                            res = "打回";
                        } else if (res === 'n') {
                            res = "拒绝";
                        }

                        confirm1 = confirm('你确认要' + res + '该申请?');
                        if (confirm1 === true) {
                            $.ajax({
                                 type : "POST",
                                 url : "/review/action/loan",
                                 data : post_data,
                                 dataType : "json",
                                 success:function(data, textstatus){
                                     $(modal_name).modal('hide');
                                     $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                                 },
                                 error:function(a,textStatus,errorThrown){
                                     $(modal_name).modal('hide');
                                     $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                                 }
                            });
                         }
                    });
                }
            },
            error:function(a,textStatus,errorThrown) {
                waitingDialog.hide();
                alert('failed');
            }
        });
    });
}

function view_loan_info(id, modal_name) {
    url = "/review/info/view/loan/" + id;
    $(modal_name).load(url, function(){
        $(modal_name).modal({backdrop: false});
        waitingDialog.hide();
        load_loan_table();
    });
}

function do_dispatch_collection(id, modal_name) {
    //url = "/review/info/view/loan/" + id;
    url = "/collection/modal/dispatch/" + id;
    $(modal_name).load(url, function(){
        //alert(url);
        $(modal_name).modal({backdrop: false});
        waitingDialog.hide();
        load_loan_table();
        $("#submit_dispatch").click(function(e) {
            var post_data = {'apply_id': $(this).attr("aid")};
            post_data["reviewer"]= $("#reviewer_select").val();
            $.ajax({
                 type : "POST",
                 url : "/collection/action/change",
                 data : post_data,
                 dataType : "json",
                 success:function(data, textstatus){
                     $(modal_name).modal('hide');
                     $('#all_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_collection"]));
                 },
                 error:function(a,textStatus,errorThrown){
                     $(modal_name).modal('hide');
                     $('#all_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param["all_collection"]));
                 }
            });
        });
    });
}

function load_repay_buttom() {
    $('input[name="repay_channel"]').change(function(e) {
        if ($(this).val() === "realtime_repay") {
            $("#upload_check_file").hide();
            $("#custom_repay_radio").show();
        } else {
            $("#upload_check_file").show();
            $("#custom_repay_radio").hide();
        }
    });

    $('input[name="repay_type"]').change(function(e) {
        if ($(this).val() === "custom") {
            $("#repay_amount_input").show();
        } else {
            $("#repay_amount_input").hide();
        }
    });
}

function load_loan_table() {
    var loan_Table = $('#loan_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["loan_table"]));
    $("#loan_table tbody").on('click','td.details-control',function(){
          var tr = $(this).closest('tr');
          var row = loan_Table.row(tr);

          if(row.child.isShown()){
              row.child.hide();
              tr.removeClass('shown')
          }else{
              row.child(loan_detail_format(row.data())).show();
              tr.addClass('shown')

              $("#loan_table tbody tr td table tbody tr td a").click(function(e){
                   var order_no = $(this).parent().parent().parent().parent().parent().parent().prev().children('td').eq(1).text();
                   var money_field = $(this).parent().parent().children('td').eq(0).text();
                   var post_data = {'order_no': order_no, 'money_field':money_field, 'token': $(this).attr("token")};
                   $.ajax({
                        type : "get",
                        url : "/custom/gen_apply_repay_type",
                        data : post_data,
                        dataType : "json",
                        success:function(data, textstatus){
                                if(data["error"] == "不能重复提交"){
                                                alert('不能重复提交');
                                                return;
                                }
				alert(data.msg);
                        },
                        error:function(a,textStatus,errorThrown){
				alert('error! '+a.statusText+a.responseXML);
                        }
                   });
              });
          }
    });
}

function load_colletion_record_table() {
    var loan_Table = $('#collection_record_table').DataTable($.mergeJsonObject(baseSettings, datatable_param["collection_record_table"]));
    $("#collection_record_table tbody").on('click','td.details-control',function(){
          var tr = $(this).closest('tr');
          var row = loan_Table.row(tr);

          if(row.child.isShown()){
              row.child.hide();
              tr.removeClass('shown')
          }else{
              row.child(loan_detail_format(row.data())).show();
              tr.addClass('shown')
          }
    });
}

function load_collection_info(id, modal_name, table_name) {
    url = "/collection/info/" + id;
    $(modal_name).load(url, function(){
        $(this).modal({backdrop: false});
        $.ajax({
            type:"GET",
            url:url,
            error:function(a,textStatus,errorThrown){
               alert('error! '+a.statusText+a.responseXML);
            },
            success:function(data, textstatus){
                $('#submit_collection').click(function(e){
                    $(this).button('loading');
                    $.ajax({
                        type:"GET",
                        url:"/collection/action/finish",
                        data: { 'type':'realtime_repay','aid': $(this).attr("aid")},
                        dataType:'json',
                        success:function(data, textstatus){
                            $(modal_name).modal("hide");
                            alert(data.msg);
                            $(table_name).dataTable($.mergeJsonObject(baseSettings, datatable_param["repay_loan"]));
                        },
                        error:function(a,textStatus,errorThrown){
                           alert('error! '+a.statusText+a.responseXML);
                        }
                    });
                });
                load_loan_table();
            }
        });
    });
}

function load_review_info(id)
{
    //url = "/review/info/" + $(obj).attr("name");
    url = "/review/info/" + id ;
    $("#review_modal").load(url, function(){
      // 创建review，验证用户信息
      $.ajax({
          type : "POST",
          url : "/review/action/add",
          data : {"apply_id": url.split("/")[3]},
          dataType : "json",
          success:function(data, textstatus){
              waitingDialog.hide();
              if (data.error) {
                alert(data.error);
                //$("#review_modal").modal('hide');
              } else {
                $("#review_modal").modal({backdrop: false});
                $("#submit_review").attr("review_id", data.review_id);
                //调整一下下对齐
                //$(obj).on('shown.bs.modal', function() {
                //    $('.review_right_panel').each(function() {
                //        $(this).css('margin-top', $(this).parent().height()-$(this).height()-20);
                //    });
                //});

                $('[data-toggle="popover"]').popover({html: true});

                $("#get_call").click(function(e) {
                  $.ajax({
                    type : "GET",
                    url : "/review/get_call",
                    data : "?uid=" + $(this).attr("uid"),
                    success:function(data, textstatus){
                        alert("请30s后下载通讯录");
                        $("#review_modal").modal('hide');
                    },
                    error:function(a,textStatus,errorThrown){
                        alert('failed');
                    }
                  });
                });

                //提交按钮
                $("#submit_review").click(function(e) {
                    //$(this).button('loading');
                    $(this).prop('disabled', true);
                    var post_data = {'apply_id': $(this).attr("apply_id"), 'review_id': $(this).attr("review_id")};
                    res = 'y';
                    $(".review_right_panel").each(function() {
                        name = $(this).attr("name");
                        post_data[name+"_notes"]= $(this).find(".notes_area").val();
                        post_data[name+"_msg"]= $(this).find(".msg_area").val();
                        post_data[name+"_radio"]= $(this).find("input[name=" + name + "]:checked").val();
                      if (res === 'y') {
                        if (post_data[name+"_radio"] !== 'y') {
                          res = post_data[name+"_radio"];
                        }
                      } else if (res === 'r') {
                        if (post_data[name+"_radio"] === 'n')  {
                          res = post_data[name+"_radio"];
                        }
                      }
                    });

                    var label_list = new Array();
                    $(".radio-inline>input:checked").each(function(e){
                        label_list.push($(this).val());
                    });

                    $(".checkbox input:checked").each(function(e){
                        label_list.push($(this).val());
                    });

                    post_data.label = label_list.join(",");

                    var comfirm1;
                    if (res === 'y') {
                        res = "通过";
                        confirm1 = confirm('你确认要通过该申请么?\r要通过该申请么?\r通过该申请么?\r通过么?\r过么?\r么?\r');
                    } else if (res === 'r') {
                        res = "打回";
                        confirm1 = confirm('你确认要' + res + '该申请?');
                    } else if (res === 'n') {
                        res = "拒绝";
                        confirm1 = confirm('你确认要' + res + '该申请?');
                    }

                    if (confirm1 === true) {
                      //  return confirm('Are you really sure?');
                      $.ajax({
                           type : "POST",
                           url : "/review/action/finish",
                           data : post_data,
                           dataType : "json",
                           success:function(data, textstatus){
                               $("#review_modal").modal('hide');
                               $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                           },
                           error:function(a,textStatus,errorThrown){
                               $("#review_modal").modal('hide');
                               $('#my_review').dataTable($.mergeJsonObject(baseSettings, datatable_param["my_review"]));
                           }
                      });
                    }
                });

                //取消按钮，删除review
                $(".cancel-btn").click(function(e) {
                   $.ajax({
                       type : "POST",
                       url : "/review/action/cancel",
                       data : {"apply_id": $("#submit_review").attr("apply_id")},
                       dataType : "json",
                       success:function(data, textstatus){
                           if (data.error) {
                             alert(data.error);
                             $("#review_modal").modal('hide');
                           } else {
                             $("#review_modal").modal('hide');
                           }
                       },
                       error:function(a,textStatus,errorThrown){
                           alert('failed');
                       }
                   });
                });

                //显示、隐藏提示信息area
                $(".recall_radio").change(function(e) {
                  $(this).siblings("textarea").show();
                  $(this).parent().parent().find(".label-group").hide();
                });

                $(".reject_radio").change(function(e) {
                  $(this).parent().parent().find(".msg_area").hide();
                  $(this).parent().parent().find(".label-group").show();
                });

                $(".pass_radio").change(function(e) {
                  $(this).parent().parent().find(".msg_area").hide();
                  $(this).parent().parent().find(".label-group").hide();
                });
              }
          },
          error:function(a,textStatus,errorThrown){
              waitingDialog.hide();
              alert('数据加载失败');
          }
      });

    });
}

function do_check(id, modal_name) {
    url = "/audit/info/check/" + id;
    $(modal_name).load(url, function() {
        $(this).modal({backdrop: false});
        $.ajax({
            type:"GET",
            url:url,
            error:function(a,textStatus,errorThrown) {
               alert('error! '+a.statusText+a.responseXML);
            },
            success:function(data, textstatus) {
                $('#confirm_check').click(function(e){
                    console.log("hahah");
                    $.ajax({
                        type:"POST",
                        url:"/audit/action/do_confirm_check",
                        data: { 'amount' : $("#amount_input").val(), 'aid' : $(this).attr("aid"),
                                'token' : $(this).attr("token"), 'notes' : $("#notes_input").val()},
                        dataType:'json',
                        success:function(data, textstatus){
                            $(modal_name).modal("hide");
                            if (data.error) {
                                alert(data.error);
                            } else {

                            }
                        },
                        error:function(a,textStatus,errorThrown){
                            alert('未知错误，请截图联系管理员');
                            $(modal_name).modal("hide");
                        }
                    });
                });

                $('#back_check').click(function(e){
                    $.ajax({
                        type:"POST",
                        url:"/audit/action/do_back_check",
                        data: { 'amount':$("#amount_input").val(), 'aid': $(this).attr("aid"),
                                'token' : $(this).attr("token"), 'notes' : $("#notes_input").val()},
                        dataType:'json',
                        success:function(data, textstatus){
                            $(modal_name).modal("hide");
                            if (data.error) {
                                alert(data.error);
                            } else {
                            }
                        },
                        error:function(a,textStatus,errorThrown){
                            alert('未知错误，请截图联系管理员');
                            $(modal_name).modal("hide");
                        }
                    });
                });
            },
        });
    });
}

function do_collection(id, modal_name) {
    url = "/collection/info/" + id;
    //url = "/operation/repay_modal/" + id;
    $("#collection_modal").load(url, function(){
        $(this).modal({backdrop: false});
        $("#check_file").fileinput({
            uploadUrl : "/collection/action/fileupload",
        });

        $('#check_file').on('fileuploaded', function(event, data, previewId, index) {
            var form = data.form, files = data.files, extra = data.extra,
                response = data.response, reader = data.reader;
            console.log('File uploaded triggered');
            //alert(response.url);
            $('#check_file').attr("url", response.url);
        });

        $.ajax({
            type:"GET",
            url:url,
            error:function(a,textStatus,errorThrown){
               alert('error! '+a.statusText+a.responseXML);
            },
            success:function(data, textstatus){
                load_repay_buttom();
                $('#submit_repayment').click(function(e){
                    submit_data = {'aid': $(this).attr("aid"), 'token': $(this).attr("token")};
                    submit_data["channel"] = $("#repay_channel_radiobox").find('input[name="repay_channel"]:checked').val();
                    submit_data["type"] = $("#repay_type_radiobox").find('input[name="repay_type"]:checked').val();
                    submit_data["url"] = $("#check_file").attr("url");
                    submit_data["notes"] = $("#check_notes").val();
                    submit_data["check_amount"] = $("#check_amount").val();
                    if(submit_data["type"] === "custom") {
                        submit_data["amount"] = $("#repay_amount_input").val();
                    } else {
                        submit_data["amount"] = $("#repay_type_" + submit_data["type"]).attr("amount");
                    }
                    //alert(submit_data["notes"], submit_data["check_amount"], submit_data["url"]);
                    submit_data["collection_check"] = $("#collection_checks").find('input[name="collection_check"]:checked').val();

                    $.ajax({
                        type:"GET",
                        url:"/collection/action/do_repay_loan",
                        data: submit_data,
                        dataType:'json',
                        success:function(data, textstatus){
                            if (data.error == 'ok') {
                                alert(data.msg);
                            } else {
                                $(this).prop('disabled', false);
                                alert(data.msg);
                            }
                            $(modal_name).modal("hide");
                            if ($("#my_collection").length > 0) {
                                $('#my_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param.my_collection));
                            } else if ($("#all_collection").length > 0) {
                                $('#all_collection').dataTable($.mergeJsonObject(baseSettings, datatable_param.all_collection));
                            }
                        },
                        error:function(a,textStatus,errorThrown){
                            alert('error! '+a.statusText+a.responseXML);
                            $(modal_name).modal("hide");
                        }
                    });
                });

                load_loan_table();
                load_colletion_record_table();

                $('#send_message').click(function(e){
                    do_sendmessage(id, "#message_modal");
                });

                $('#do_reduction').click(function(e){
                    do_reduction(id, "#message_modal");
                });


                $('#repay_time').daterangepicker({
                    "singleDatePicker": true,
                    "timePicker24Hour": true,
                    "timePicker": true,
                    "autoApply": true,
                }, function(start, end, label) {
                    //alert('A date range was chosen: ' + start.format('YYYY-MM-DD hh:mm') + ' to ' + end.format('YYYY-MM-DD hh:mm'));
                    $("#config-repay_time").val(start.format('YY-MM-DD HH:mm:ss'));
                });

                $('#submit_collection_record').click(function(e){
                    add_collection_record(id, "#collection_record_table");
                });

            }
        });
    });
}

function view_review_info(id, modal_name) {
    url = "/review/info/view/" + id
    $(modal_name).load(url, function(){
      $(this).modal({backdrop: false});
      ////调整一下下对齐
      //$(this).on('shown.bs.modal', function() {
      //    $('.review_right_panel').each(function() {
      //        $(this).css('margin-top', $(this).parent().height()-$(this).height()-20);
      //    });
      //});
      $('[data-toggle="popover"]').popover({html: true});
      waitingDialog.hide();

      $("#reset_review").click(function(){
          json_data = {'apply_id':id, 'token': $(this).attr("token")},
          $.ajax({
              type:"POST",
              url:"/review/action/reset_review",
              data: json_data,
              dataType:'json',
              success:function(data, textstatus){
                  if (data.error) {
                      alert(data.error);
                  } else {
                      alert(data.result);
                  }
                  $(modal_name).modal("hide");
              },
              error:function(a,textStatus,errorThrown){
                  $(modal_name).modal("hide");
                  alert("系统错误 重置失败");
              }
          });
      });
    });
}

function do_reduction(id, modal_name) {
    url = "/collection/modal/reduction/" + id;
    $(modal_name).load(url, function(){
        $(this).modal({backdrop: false});
        $.ajax({
            type:"GET",
            url:url,
            error:function(a,textStatus,errorThrown){
               alert('error! '+a.statusText+a.responseXML);
            },
            success:function(data, textstatus){
                $('#submit_reduction').click(function(e){
                    $(this).prop('disabled', true);
                    $.ajax({
                        type:"POST",
                        url:"/collection/action/reduction",
                        data: { 'amount': $("#reduction_amount").val(), 'reason': $("#reduction_reason").val(),
                                'apply':id, 'token': $(this).attr("token")},
                        dataType:'json',
                        success:function(data, textstatus){
                            $(modal_name).modal("hide");
                            if (data.error) {
                                alert(data.error);
                            } else {
                                alert(data.result);
                                $("#reduction_column").html($("#reduction_amount").val());
                                rest = (parseFloat($("#rest_column").html()) - parseFloat($("#reduction_amount").val()));
                                $("#rest_column").html(rest);
                            }
                            $('#collection_record_table').dataTable($.mergeJsonObject(baseSettings, datatable_param["collection_record_table"]));
                        },
                        error:function(a,textStatus,errorThrown){
                            $(modal_name).modal("hide");
                            alert("减免失败");
                        }
                    });
                });
                $('#cancel_reduction').click(function(e){
                    $(modal_name).modal("hide");
                });
            }
        });
    });
}

function do_sendmessage(id, modal_name) {
    url = "/collection/modal/message/" + id;
    //alert(modal_name);
    $(modal_name).load(url, function(){
        $(this).modal({backdrop: false});
        $.ajax({
            type:"GET",
            url:url,
            error:function(a,textStatus,errorThrown){
               alert('error! '+a.statusText+a.responseXML);
            },
            success:function(data, textstatus){
                $('#submit_message').click(function(e){
                    $(this).prop('disabled', true);
                    $.ajax({
                        type:"POST",
                        url:"/collection/action/sendmessage",
                        data: { 'phone_no': $("#phone_no_to_send").val(),'content': $("#content_to_send").val(),
                                'apply':id, 'token': $(this).attr("token")},
                        dataType:'json',
                        success:function(data, textstatus){
                            $(modal_name).modal("hide");
                            if (data.error) {
                                alert(data.error);
                            }
                            $('#collection_record_table').dataTable($.mergeJsonObject(baseSettings, datatable_param["collection_record_table"]));
                        },
                        error:function(a,textStatus,errorThrown){
                            $(modal_name).modal("hide");
                            alert("系统错误 短信发送失败");
                            //alert('error! '+a.statusText+a.responseXML);
                        }
                    });
                });
                $('#cancel_message').click(function(e){
                    $(modal_name).modal("hide");
                });
                $('.message-phone').click(function(e){
                    var phone_no = $(this).attr("phone");
                    $("#phone_no_to_send").val(phone_no);
                    $(this).siblings().removeClass("btn-primary");
                    $(this).siblings().removeClass("btn-default");
                    $(this).siblings().addClass("btn-default");
                    $(this).addClass("btn-primary");
                });
            }
        });
    });
}

function add_collection_record_from_repay(id, table_name) {
    $.ajax({
        type:"POST",
        url:"/operation/add_collection_record",
        data: {'apply':id, 'content':$("#collection_record").val(),
               'object':$("#repay_type_radio").find("input[name=repay_type]:checked").val(), 'time':"", },
        dataType:'json',
        success:function(data, textstatus){
            alert('标记添加成功');
            $('#collection_record_table').dataTable($.mergeJsonObject(baseSettings, datatable_param["collection_record_table"]));
        },
        error:function(a,textStatus,errorThrown){
        }
    });
}

function add_collection_record(id, table_name) {
    var request_data = {'apply':id, 'content':$("#collection_record").val(), 'object':$("#repay_type_radio").find("input[name=repay_type]:checked").val(), 'time':$("#config-repay_time").val(), 'token': $(this).attr("token")};
    $.ajax({
        type:"POST",
        url:"/collection/action/add_collection_record",
        data: request_data,
        dataType:'json',
        success:function(data, textstatus){
            $('#collection_record_table').dataTable($.mergeJsonObject(baseSettings, datatable_param["collection_record_table"]));
        },
        error:function(a,textStatus,errorThrown){
        }
    });
}

$.mergeJsonObject = function(jsonbject1, jsonbject2) {
    var resultJsonObject={};
    for(var attr in jsonbject1){
        resultJsonObject[attr]=jsonbject1[attr];
    }
    for(var attr in jsonbject2){
        if (attr === "language") { //deep merge
            for (var sub in jsonbject2[attr]) {
                resultJsonObject[attr][sub] = jsonbject2[attr][sub];
            }
        } else {
            resultJsonObject[attr]=jsonbject2[attr];
        }
    }
    return resultJsonObject;
};


