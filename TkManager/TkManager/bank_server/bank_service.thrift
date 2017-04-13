namespace cpp bank_service
namespace java bank_service

struct CardVerifyRequest {
  1: string card_id,
  2: optional string owner_name,
  3: i64 user_id,
  4: optional string phone_number,
}

struct CardVerifyResponse {
  1: i32 retcode,
  2: optional string err_msg,
  3: optional string bank_name,
  4: optional i32 bank_type,
}

struct RealtimePay {
  1: i32 amount,
  2: string bank_code,
  3: string account_cardid,
  4: string account_name,
  5: i64 user_id,
  6: string pay_type,  //xintuo, mifan
}

struct RealtimePayFor {
  1: i32 amount,
  2: string bank_code,
  3: string account_cardid,
  4: string account_name,
  5: i64 user_id,
}

struct CommonResponse {
  1: i32 retcode,
  2: optional string err_msg,
}

struct BatchPay {
  1: list<RealtimePay> pay_user_list,
}

service BankService {
  CardVerifyResponse card_verify(1:CardVerifyRequest request),
  CommonResponse realtime_pay(1:RealtimePay request),
  CommonResponse realtime_payfor(1:RealtimePayFor request),
  i32 batch_pay(1:BatchPay request)
}
