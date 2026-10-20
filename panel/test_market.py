"""Fixtures artificiales: no consultas de mercado ni carga de modelos."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from market import MarketLedger,HOUR,score,digest,validate_candles


class ControlTests(unittest.TestCase):
    def test_score_keeps_direction_separate_from_price(self):
        good=score(100,101,102)
        self.assertTrue(good['direction_correct']);self.assertEqual(good['price_score'],50)
        bad=score(100,110,101)
        self.assertTrue(bad['direction_correct']);self.assertLess(bad['price_score'],0)
        self.assertIsNone(score(100,101,100)['price_score'])
        self.assertFalse(score(100,99,102)['direction_correct'])

    def test_open_candles_and_gaps(self):
        def row(start):return [start,'100','102','99','101','10',start+HOUR-1,'1000']
        self.assertEqual(len(validate_candles([row(0),row(HOUR)],HOUR)),1)
        with self.assertRaises(ValueError):validate_candles([row(0),row(2*HOUR)],4*HOUR)

    def test_reject_sealing_after_target_already_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=MarketLedger(tmp);folder=Path(tmp)/'late';folder.mkdir()
            (folder/'context.json').write_text(json.dumps(dict(cutoff_ms=HOUR)))
            (folder/'generated.json').write_text('{}')
            with patch('market.get_public',return_value=({'serverTime':2*HOUR},{})):
                with self.assertRaises(ValueError):ledger.seal(folder)
            self.assertFalse((folder/'forecast.json').exists())

    def test_never_score_future_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger=MarketLedger(tmp);folder=Path(tmp)/'fixture';folder.mkdir()
            forecast=[dict(horizon=i,target_close_ms=(i+1)*HOUR,kronos_close=101,
                timesfm_close=103,ensemble_close=102,kronos_up_fraction=.75,
                timesfm_q10=99,timesfm_q90=104) for i in range(1,5)]
            prediction=dict(id='fixture',base=100,issued_ms=HOUR+1000,cutoff_ms=HOUR,forecast=forecast)
            ledger.exclusive(folder/'forecast.json',dict(prediction=prediction,sha256=digest(prediction)))
            with patch('market.get_public',return_value=({'serverTime':2*HOUR-100},{'url':'fixture'})) as request:
                ledger.reconcile();self.assertEqual(request.call_count,1)
            self.assertEqual(ledger.records()[0]['evaluations'],[])
            candle=[HOUR,'100','103','99','102','10',2*HOUR-1,'1000']
            with patch('market.get_public',side_effect=[({'serverTime':2*HOUR+3000},{}),([candle],{'url':'fixture'})]):
                ledger.reconcile()
            evaluated=ledger.records()[0]['evaluations'];self.assertEqual(len(evaluated),1)
            self.assertEqual(evaluated[0]['models']['ensemble']['absolute_error_usdt'],0)
            self.assertEqual(evaluated[0]['horizon'],1)
            with self.assertRaises(FileExistsError):ledger.exclusive(folder/'evaluation-1.json',{})
            obj=json.loads((folder/'forecast.json').read_text());obj['prediction']['base']=999
            (folder/'forecast.json').write_text(json.dumps(obj))
            with self.assertRaises(ValueError):ledger.records()


if __name__=='__main__':unittest.main()
