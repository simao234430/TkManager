namespace cpp fetch_thirdparty
namespace java fetch_thirdparty

struct BindThirdpartyRequest {
  1: string uid,
  2: string access_token,
  3: i32 bind_type,
  4: i64 user_id,
}

struct SendCaptchaRequest {
  1: string captcha,
  2: i64 user_id,
}

struct RebindChsiResponse {
  1: i32 retcode,     #0:直接拉取成功，无需后续操作. -1:需要填验证码. -2:其他原因导致拉取失败
  2: optional string captcha,
  3: optional string errmsg,
}

service BindThirdpartyService {
  i32 bind_thirdparty(1:BindThirdpartyRequest request),
  RebindChsiResponse send_captcha(1:SendCaptchaRequest request),
  RebindChsiResponse rebind_chsi(1:i64 user_id)
}
