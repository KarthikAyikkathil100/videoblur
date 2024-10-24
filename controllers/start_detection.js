const aws = require('aws-sdk');


const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition({ region: 'us-east-1' });
const s3 = new AWS.S3();

const jobType = {
    FACE: 'face',
    label: 'label'
}
exports.handler = async (event) => {
    try {
        // Extract S3 bucket and video key from the event
        const bucket = 'project-videostore';
        console.log('event => ', event)
        const key = event['file_name']

        let reqJobType = jobType.FACE;
        if (event['job_type'] && event['job_type'] === jobType.label) reqJobType = jobType.label;

        // Parameters for the Rekognition video job
        const params = {
            Video: {
                S3Object: {
                    Bucket: bucket,
                    Name: key
                }
            },
            JobTag: reqJobType === jobType.FACE ? 'FaceDetectionJob' : 'LabelDetectionJob',
            FaceAttributes: 'ALL',
            
        };

        // Start the Rekognition video analysis job

        let result = null;
        if (reqJobType === jobType.FACE) {
            result = await rekognition.startFaceDetection(params).promise()
        } else {
            delete params.FaceAttributes;
            result = await rekognition.startLabelDetection(params).promise()
        }
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
