const fs = require('fs');
const path = require('path');
const { MongoClient } = require('mongodb');
const { ServerApiVersion } = require('mongodb');

// MongoDB连接字符串
const uri = "mongodb+srv://kelosaner:OvWIRlio37zB0fKG@cluster0.bi4livc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
const socksOptions = {
    proxyHost: "127.0.0.1",
    proxyPort: 1080,
  };
// MongoDB数据库名
const dbName = "hansproject";
// 集合名称
const collectionName = "hansdata";
// JSON文件所在目录
// 获取根目录i
const rootDirectory = path.resolve(__dirname, '../..');
const jsonDirectory = path.join(rootDirectory, '/output/parsed_json');

// 创建MongoDB客户端
const client = new MongoClient(uri, socksOptions, {
    serverApi: {
      version: ServerApiVersion.v1,
      strict: true,
      deprecationErrors: true,
    }
  });

async function main() {
    try {
        // 连接到MongoDB
        await client.connect();
        const database = client.db(dbName);
        const collection = database.collection(collectionName);

        // 读取目录中的所有文件
        const files = fs.readdirSync(jsonDirectory);

        // 遍历文件
        for (let file of files) {
            // 确保只处理JSON文件
            if (path.extname(file) === '.json') {
                const filePath = path.join(jsonDirectory, file);
                const fileContent = fs.readFileSync(filePath);
                const data = JSON.parse(fileContent);

                // 插入数据到MongoDB
                await collection.insertMany(data);
                console.log(`Data from ${file} has been inserted.`);
            }
        }
    } catch (error) {
        console.error('An error occurred:', error);
    } finally {
        // 关闭数据库连接
        await client.close();
    }
}

main();