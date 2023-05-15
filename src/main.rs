use serde::{Deserialize, Serialize};
use std::env;
use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::str;

#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, PartialOrd)]
struct Temp(f32);
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, PartialOrd)]
struct Pres(f32);
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, PartialOrd)]
struct Humi(f32);
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, PartialOrd)]
struct Free(f32);

impl Eq for Temp{}
impl Eq for Pres{}
impl Eq for Humi{}
impl Eq for Free{}

impl Ord for Temp{
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.0.total_cmp(&other.0)
    }
}
impl Ord for Pres{
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.0.total_cmp(&other.0)
    }
}
impl Ord for Humi{
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.0.total_cmp(&other.0)
    }
}
impl Ord for Free{
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        self.0.total_cmp(&other.0)
    }
}

#[derive(Debug, Deserialize, Serialize, Clone)]
struct Data(u32, Temp, Pres, Humi, Free); 

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
    // println!("{:?}", server_data);

    let tn = server_data.iter().min_by_key(|d| &d.1).unwrap();
    println!("min: {:?}", tn.1);
    let tx = server_data.iter().max_by_key(|d| &d.1).unwrap();
    println!("max: {:?}", tx.1);

    let pn = server_data.iter().min_by_key(|d| &d.2).unwrap();
    println!("min: {:?}", pn.2);
    let px = server_data.iter().max_by_key(|d| &d.2).unwrap();
    println!("max: {:?}", px.2);

    let hn = server_data.iter().min_by_key(|d| &d.3).unwrap();
    println!("min: {:?}", hn.3);
    let hx = server_data.iter().max_by_key(|d| &d.3).unwrap();
    println!("max: {:?}", hx.3);

    let mn = server_data.iter().min_by_key(|d| &d.4).unwrap();
    println!("min: {:?}", mn.4);
    let mx = server_data.iter().max_by_key(|d| &d.4).unwrap();
    println!("max: {:?}", mx.4);
}
