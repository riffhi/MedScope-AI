import { Client, Databases, Storage, ID } from "appwrite";

const endpoint = import.meta.env.VITE_APPWRITE_ENDPOINT;
const projectId = import.meta.env.VITE_APPWRITE_PROJECT_ID;
const databaseId = import.meta.env.VITE_APPWRITE_DATABASE_ID;
const storageBucketId = import.meta.env.VITE_APPWRITE_BUCKET_ID; 

const collections = {
  scans: import.meta.env.VITE_APPWRITE_SCANS_COLLECTION_ID,

};

if (
  !endpoint ||
  !projectId ||
  !databaseId ||
  !storageBucketId ||
  !collections.scans
) {
  throw new Error(
    "Missing Appwrite environment variables. Please check your .env.local file and ensure all VITE_ variables are set."
  );
}

const client = new Client();
client.setEndpoint(endpoint).setProject(projectId);

export const databases = new Databases(client);
export const storage = new Storage(client); 
export const AppwriteID = ID;

export const APPWRITE_CONFIG = {
  databaseId,
  storageBucketId,
  collections,
};
