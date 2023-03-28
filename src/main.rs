use std::net::TcpStream;
use std::str;
use std::io::{BufRead, BufReader, Write};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct SensorData(u32, f32);

#[derive(Debug, Deserialize, Serialize)]
struct ServerData(Vec<SensorData>);

fn main() {
    println!("GETTEMP....");
    println!("Connecting....");
    let mut stream = TcpStream::connect("127.0.0.1:65510")
    // let mut stream = TcpStream::connect("192.168.43.169:65510")
    // let mut stream = TcpStream::connect("192.168.43.149:65510")
                               .expect("Could not connect to server");
    let cmd = "GETTEMP\n";
    println!("Sending command....");
    stream.write(cmd.as_bytes()).expect("Failed to write to server");

    let mut reader = BufReader::new(&stream);

    let mut buffer: Vec<u8> = vec![];
    println!("Reading....");
    reader.read_until(b'\n', &mut buffer).expect("Could not read into buffer");

    let str1 = str::from_utf8(&buffer).expect("Could not write buffer as string");
    println!("{}", str1);

    let server_data: ServerData = serde_json::from_str(str1).unwrap();
    println!("{:?}", server_data);
}
