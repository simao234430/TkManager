namespace cpp message_service
namespace java message_service

struct SendMessageRequest {
  1: string phone_number,
  2: string content,
  3: optional string send_time,
  4: i32 msg_type,
}

struct SendContractRequest {
  1: string contract_url,
  2: i64 user_id,
  3: string to_email,
}

service MessageService {
  i32 send_message(1:SendMessageRequest request),
  i32 send_contract(1:SendContractRequest request)
}
