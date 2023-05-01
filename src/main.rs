use std::net::TcpStream;
use std::str;
use std::io::{BufRead, BufReader, Write};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Deserialize, Serialize)]
struct SensorData(u32, f32, f32, f32, f32);

#[derive(Debug, Deserialize, Serialize)]
struct ServerData(Vec<SensorData>);

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 1 {
        println!("Add ip address and port to the command line  aa:bb:cc:dd:pp");
        std::process::exit(0);
    }
    let address = &args[1];

    let mut stream = TcpStream::connect(address)
                               .expect("Could not connect to server");
    let cmd = "GETTEMP\n";
    println!("Sending command {cmd}");
    stream.write(cmd.as_bytes()).expect("Failed to write to server");

    let mut reader = BufReader::new(&stream);

    let mut buffer: Vec<u8> = vec![];
    println!("Reading...");
    reader.read_until(b'\n', &mut buffer).expect("Could not read into buffer");

    let str1 = str::from_utf8(&buffer).expect("Could not write buffer as string");
    println!("{}", str1);

    let server_data: ServerData = serde_json::from_str(str1).unwrap();
    println!("{:?}", server_data);
}
