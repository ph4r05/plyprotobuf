import plyproto.parser as plyproto

test1 = """package tutorial;"""

test2 = """package tutorial;

message Person {
  required string name = 1;
  required int32 id = 2;
  optional string email = 3;
}

"""

test3 = """package tutorial;
option java_outer_classname = "PushNotifications";
option optimize_for = "SPEED";

  message Person {
      required string name = 1;
      required int32 id = 2;
      optional string email = 3;

      enum PhoneType {
        MOBILE = 0;
        HOME = 1;
        WORK = 2;
      }

      message PhoneNumber {
        required string number = 1;
        optional PhoneType type = 2 [default = HOME];
      }

      repeated PhoneNumber phone = 4;
      extensions 500 to 990;
}

message AddressBook {
  repeated Person person = 1;

  // Possible extension numbers.
  extensions 500 to max;
}"""

parser = plyproto.ProtobufAnalyzer()
print(parser.parse_string(test3))
