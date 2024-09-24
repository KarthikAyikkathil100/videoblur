const aws = require('aws-sdk');


const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition({ region: 'us-east-1' });
const s3 = new AWS.S3();

exports.handler = async (event) => {
    try {
        // Extract S3 bucket and video key from the event
        const bucket = 'project-videostore';
        const key = 'walking_speed_format.mov';

        // Parameters for the Rekognition video job
        const params = {
            Video: {
                S3Object: {
                    Bucket: bucket,
                    Name: key
                }
            },
            JobTag: 'FaceDetectionJob',
            FaceAttributes: 'ALL'
        };

        // Start the Rekognition video analysis job
        const result = await rekognition.startFaceDetection(params).promise();
        console.log('Face detection job started:', result);

        return {
            statusCode: 200,
            body: JSON.stringify(result),
        };
    } catch (error) {
        console.error('Error starting face detection job:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: error.message }),
        };
    }
};
