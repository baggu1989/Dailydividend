# schedule_news.py

import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from app.news_fetcher import fetch_combined_news, process_and_store, get_news_statistics
from app.logging.logger import logger
from app.config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from app.marketaux_client import marketaux_client


class EnhancedNewsScheduler:
    """Enhanced news scheduler with multiple frequencies and source management"""
    
    def __init__(self):
        self.last_run = {}
        self.run_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "articles_fetched": 0,
            "last_successful_run": None
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup enhanced logging for the scheduler"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
    
    def fetch_by_frequency(self, frequency: str):
        """Fetch news based on update frequency"""
        logger.info(f" Starting {frequency} news fetch...")
        
        try:
            logger.info(f" Fetching news with {frequency} frequency")
            
            # Fetch news from both Yahoo Finance RSS and MarketAux
            news = fetch_combined_news()
            #market_aux_news = pr()
            if news:
                process_and_store(news)
                self.run_stats["articles_fetched"] += len(news)
                self.run_stats["successful_runs"] += 1
                self.run_stats["last_successful_run"] = datetime.now()
                logger.info(f" {frequency} fetch completed successfully - {len(news)} articles")
            else:
                logger.warning(f" {frequency} fetch completed but no articles found")
                
        except Exception as e:
            self.run_stats["failed_runs"] += 1
            logger.error(f" {frequency} fetch failed: {str(e)}")
        
        self.run_stats["total_runs"] += 1
        self.last_run[frequency] = datetime.now()
    
    def hourly_job(self):
        """Fetch from hourly sources"""
        self.fetch_by_frequency("hourly")
    
    def daily_job(self):
        """Fetch from daily sources"""
        self.fetch_by_frequency("daily")
    
    def weekly_job(self):
        """Fetch from weekly sources"""
        self.fetch_by_frequency("weekly")
    
    def full_fetch_job(self):
        """Fetch from all sources (comprehensive update)"""
        logger.info(" Starting comprehensive news fetch...")
        
        try:
            # Fetch all news from both sources
            news = fetch_combined_news()
            #articles = marketaux_client.get_news_sentiment(limit=100)
            combined = (news or []) #+ (articles or [])  # Increase limit as needed
            if combined:
                process_and_store(news)
                self.run_stats["articles_fetched"] += len(news)
                self.run_stats["successful_runs"] += 1
                self.run_stats["last_successful_run"] = datetime.now()
                
                # Get news statistics
                news_stats = get_news_statistics()
                logger.info(f"Comprehensive fetch completed - {len(news)} articles")
                logger.info(f"Vector store now contains {news_stats.get('total_documents', 'unknown')} documents")
            else:
                logger.warning("Comprehensive fetch completed but no articles found")
                
        except Exception as e:
            self.run_stats["failed_runs"] += 1
            logger.error(f" Comprehensive fetch failed: {str(e)}")
        
        self.run_stats["total_runs"] += 1
    
    def health_check_job(self):
        """Perform health check and report statistics"""
        logger.info(" Performing health check...")
        
        try:
            # Get current statistics
            news_stats = get_news_statistics()
            
            # Calculate success rate
            success_rate = (self.run_stats["successful_runs"] / self.run_stats["total_runs"] * 100) if self.run_stats["total_runs"] > 0 else 0
            
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "scheduler_stats": self.run_stats,
                "success_rate": f"{success_rate:.1f}%",
                "news_stats": news_stats,
                "last_runs": {k: v.isoformat() if v else None for k, v in self.last_run.items()}
            }
            
            logger.info(" Health Check Report:")
            logger.info(f"   Total Runs: {self.run_stats['total_runs']}")
            logger.info(f"   Success Rate: {success_rate:.1f}%")
            logger.info(f"   Articles Fetched: {self.run_stats['articles_fetched']}")
            logger.info(f"   Vector Store Documents: {news_stats.get('total_documents', 'unknown')}")
            
            return health_report
            
        except Exception as e:
            logger.error(f" Health check failed: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_job(self):
        """Cleanup old data and remove all existing content in Chroma DB"""
        logger.info("Starting cleanup job...")
        try:
            embedder = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
            vectorstore = Chroma(persist_directory=settings.CHROMA_PATH, embedding_function=embedder)
            collection = vectorstore._collection

            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            #import pdb;pdb.set_trace()
            # Get all IDs and delete them
            result = collection.get(include=["metadatas", "ids"])
            ids_to_delete = []
            for idx, metadata in enumerate(result.get("metadatas", [])):
                doc_date = metadata.get("date")
                if doc_date and doc_date < cutoff_date:
                    ids_to_delete.append(result["ids"][idx])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.info(f"Cleanup completed: Removed {len(ids_to_delete)} documents older than 30 days from Chroma DB.")
            else:
                logger.info("Cleanup completed: No month-old documents found in Chroma DB.")
                # all_ids = result.get("ids", [])
            # if all_ids:
            #     collection.delete(ids=all_ids)
            #     logger.info("Cleanup completed: All content removed from Chroma DB.")
            # else:
            #     logger.info("Cleanup completed: No documents found in Chroma DB.")

        except Exception as e:
            logger.error(f" Cleanup failed: {str(e)}")
    
    def setup_schedule(self):
        """Setup the scheduling configuration"""
        logger.info("Setting up enhanced news scheduler...")
        
        # Schedule based on update frequencies
        schedule.every().hour.do(self.hourly_job)
        schedule.every().day.at("06:00").do(self.daily_job)
        schedule.every().sunday.at("08:00").do(self.weekly_job)
        
        # Comprehensive fetch every 6 hours
        schedule.every(6).hours.do(self.full_fetch_job)
        
        # Health check every 2 hours
        schedule.every(2).hours.do(self.health_check_job)
        
        # Cleanup every day at 2 AM
        #schedule.every().day.at("02:00").do(self.cleanup_job)
        
        logger.info(" Schedule configured:")
        logger.info("    Hourly sources: Every hour")
        logger.info("    Daily sources: 6:00 AM daily")
        logger.info("    Weekly sources: 8:00 AM Sundays")
        logger.info("    Comprehensive fetch: Every 6 hours")
        logger.info("    Health check: Every 2 hours")
        logger.info("    Cleanup: 2:00 AM daily")
    
    def run(self):
        """Run the scheduler"""
        logger.info(" Starting Enhanced News Scheduler...")
        self.cleanup_job()
        # Initial setup
        self.setup_schedule()
        
        # Perform initial fetch
        logger.info(" Performing initial fetch...")
        self.full_fetch_job()
        
        # Health check
        #elf.health_check_job()
        
        logger.info(" Scheduler is now running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.health_check_job()  # Final health check
        except Exception as e:
            logger.error(f" Scheduler error: {str(e)}")
            raise

def main():
    """Main function to run the enhanced scheduler"""
    scheduler = EnhancedNewsScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()
