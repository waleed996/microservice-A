import os

import rabbitpy


class QueueHelper:
    rabbitmq_host = os.getenv('RABBITMQ_HOST', '127.0.0.1')
    rabbitmq_port = os.getenv('RABBITMQ_PORT', 5672)

    @staticmethod
    def send_to_audio_queue(data: bytes, queue_name='audio-parts') -> None:
        """
        Send data to audio queue

        :param data: bytes audio data that needs to be sent to the queue
        :param queue_name: name of the queue to send data to
        """

        # Assume we have error handling for connection related errors here
        with rabbitpy.Connection(f'amqp://{QueueHelper.rabbitmq_host}:{QueueHelper.rabbitmq_port}/') as conn:
            with conn.channel() as channel:
                rabbitpy.Queue(channel, queue_name)
                message = rabbitpy.Message(channel, data)

                # Send to queue
                message.publish('', queue_name)

    @staticmethod
    def get_message_from_queue(queue_name: str) -> str or None:
        """
        Get a message from queue

        :param queue_name: name of the queue to receive data from
        :return: json serialized string
        """

        with rabbitpy.Connection(f'amqp://{QueueHelper.rabbitmq_host}:{QueueHelper.rabbitmq_port}/') as conn:
            with conn.channel() as channel:
                queue = rabbitpy.Queue(channel, queue_name)

                message = queue.get()
                if message:
                    # send ack that message is received and can be removed from the queue
                    message.ack()
                    return message.body
                else:
                    return None

