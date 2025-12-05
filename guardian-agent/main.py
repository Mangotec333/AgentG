"""
Guardian Agent - Main entry point.
Local agent that collects workflow telemetry and sends to cloud.
"""
import time
import signal
import sys
import os
from threading import Thread

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.logger import guardian_logger
from guardian_agent.config import config
from guardian_agent.event_collector import EventCollector
from guardian_agent.filesystem_watcher import FilesystemWatcher
from guardian_agent.batch_sender import BatchSender


class GuardianAgent:
    """Main Guardian Agent class."""
    
    def __init__(self):
        self.event_collector = EventCollector()
        self.filesystem_watcher = FilesystemWatcher(self.event_collector)
        self.batch_sender = BatchSender()
        self.running = False
        self.send_thread = None
    
    def start(self):
        """Start the Guardian Agent."""
        guardian_logger.info("Starting Guardian Agent...")
        guardian_logger.info(f"Agent ID: {config.agent_id}")
        guardian_logger.info(f"Workspace ID: {config.workspace_id}")
        guardian_logger.info(f"Ingestion Endpoint: {config.ingestion_endpoint}")
        
        self.running = True
        
        # Start filesystem watcher
        self.filesystem_watcher.start()
        
        # Start batch sender thread
        self.send_thread = Thread(target=self._batch_sender_loop, daemon=True)
        self.send_thread.start()
        
        guardian_logger.info("Guardian Agent started successfully")
    
    def stop(self):
        """Stop the Guardian Agent."""
        guardian_logger.info("Stopping Guardian Agent...")
        self.running = False
        
        # Stop filesystem watcher
        self.filesystem_watcher.stop()
        
        # Send remaining events
        self._flush_events()
        
        guardian_logger.info("Guardian Agent stopped")
    
    def _batch_sender_loop(self):
        """Background thread that periodically sends batched events."""
        while self.running:
            try:
                # Get batch of events
                batch = self.event_collector.get_batch()
                
                if batch:
                    self.batch_sender.send_batch(batch)
                
                # Wait for next interval
                time.sleep(config.batch_interval_seconds)
            
            except Exception as e:
                guardian_logger.error(f"Error in batch sender loop: {e}")
                time.sleep(config.batch_interval_seconds)
    
    def _flush_events(self):
        """Flush all remaining events."""
        guardian_logger.info("Flushing remaining events...")
        while True:
            batch = self.event_collector.get_batch()
            if not batch:
                break
            self.batch_sender.send_batch(batch)
        
        stats = self.batch_sender.get_stats()
        guardian_logger.info(f"Final stats: {stats}")


def main():
    """Main entry point."""
    agent = GuardianAgent()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        guardian_logger.info("Received shutdown signal")
        agent.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        agent.start()
        
        # Keep running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        agent.stop()
    except Exception as e:
        guardian_logger.error(f"Fatal error: {e}")
        agent.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()

