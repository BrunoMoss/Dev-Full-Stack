from pydantic import BaseModel
from typing import Optional, List

class OptimizatonSchema(BaseModel):
    """ Define os parêmetros da otimização
    """
    asset_list: Optional[str] = 'SQQQ,SPY,FXI'
    n_assets_portfolio: float = 10
    
    


