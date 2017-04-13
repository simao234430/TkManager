

### models 介绍
app拆成了三个 order review collection <br/>
order主要是用户的申请<br/>
review主要是审批人员审批的结果<br/>
operation主要是运营相关的(打款 扣款)<br/>
collection主要是催收相关的<br/>
员工管理主要是权限相关的<br/>

其实相互之间的耦合还是非常紧的，确实不太好拆

order中的user是用户基本表，其他的表都是外键关联过来的, user和其他表的关系是一对多, 或者一对一<br/>
order中另一张核心表是apply，一个user可以有多个apply，所有apply都会按照类型弹给审批系统中的不同工作人员<br/>

review中的核心表是review，review和apply是多对一的关系，一个apply最近一个review是正在处理/完成该订单的人，可以被高权限的调整分配给其他人。老的review会保留，做绩效核算用。

review下面有多条reviewrecord


apply有的从risk_management_server创建，也有催收成给运营的
