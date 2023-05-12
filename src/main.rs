use serde::{Deserialize, Serialize};
use std::env;
use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::str;

#[derive(Debug, Deserialize, Serialize, Clone)]
struct Data(u32, f32, f32, f32, f32); // time, temp, press, humidity, free

impl Data {
    fn get_temprature(&self) -> f32 {
        self.1
    }

    fn _get_pressure(&self) -> f32 {
        self.2
    }

    fn min(data: &[Data], f: fn(&Data) -> f32) -> Data {
        data.iter()
            .reduce(|a, b| if f(a) < f(b) { a } else { b })
            .unwrap_or(&Data(0, f32::MAX, f32::MAX, f32::MAX, f32::MAX))
            .clone()
    }

    fn max(data: &[Data], f: fn(&Data) -> f32) -> Data {
        data.iter()
            .reduce(|a, b| if f(a) > f(b) { a } else { b })
            .unwrap_or(&Data(0, f32::MIN, f32::MIN, f32::MIN, f32::MIN))
            .clone()
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 1 {
        println!("Add ip address and port to the command line  aa:bb:cc:dd:pp");
        std::process::exit(0);
    }
    let address = &args[1];

    let mut stream = TcpStream::connect(address).expect("Could not connect to server");
    let cmd = "GETTEMP\n";
    println!("Sending command {cmd}");
    stream
        .write(cmd.as_bytes())
        .expect("Failed to write to server");

    let mut reader = BufReader::new(&stream);

    let mut buffer: Vec<u8> = vec![];
    println!("Reading...");
    reader
        .read_until(b'\n', &mut buffer)
        .expect("Could not read into buffer");

    let str1 = str::from_utf8(&buffer).expect("Could not write buffer as string");
    // println!("{}", str1);

    let server_data: Vec<Data> = serde_json::from_str(str1).unwrap();
    println!("{:?}", server_data);

    let tn = Data::min(&server_data, Data::get_temprature);
    println!("min: {}", tn.get_temprature());

    let tx = Data::max(&server_data, Data::get_temprature);
    println!("max: {}", tx.get_temprature());
}
