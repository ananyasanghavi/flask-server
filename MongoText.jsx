import {MongoClient} from 'mongodb';
import dotenv from 'dotenv';
const util = require('util');
require('util.promisify').shim();
const accountSid = process.env.ACCOUNT_SID;
const authToken = process.env.AUTH_TOKEN;
const client = require('twilio')(accountSid, authToken);
const connectAsync = util.promisify(MongoClient.connect);
dotenv.config();
// Connection URI
const uri = process.env.MONGO_URL;
// const clientDB = new MongoClient(uri);

async function MongoText() {
    let client;
    try {
        // Connect to the MongoDB client
        client = await connectAsync(uri);
        console.log('Connected to the database');

        // Specify the database and collection
        const database = client.db('test');
        const collection = database.collection('numbers');

        // Fetch recipient number from MongoDB
        const recipientDocument = await collection.findOne({phoneNumber}); 
        console.log(phoneNumber)
        // You need to specify your query criteria here
        const recipientNumber = recipientDocument.phoneNumber;

        // Send the message
        const messageBody = 'Your condition has been detected!';
        await client.messages.create({
            body: messageBody,
            from: process.env.PHONE_NUMBER,
            to: recipientNumber
        });
        console.log('Message sent successfully');
    } catch (error) {
        console.error('Error occurred:', error);
    } finally {
        // Close the connection
        await clientDB.close();
    }
}

// Call the main function
export default MongoText;
